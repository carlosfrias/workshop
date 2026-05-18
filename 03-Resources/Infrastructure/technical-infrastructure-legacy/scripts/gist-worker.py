#!/usr/bin/env python3
"""
gist-worker.py — Autonomous Gist polling worker for lab nodes
Part of TI-011 meta-orchestration (off-premise remote access)

Polls a GitHub Gist for tasks, executes them, posts results back.
Works through firewalls — only needs HTTPS outbound.

Installation:
    sudo cp gist-worker.py /usr/local/bin/
    sudo chmod +x /usr/local/bin/gist-worker.py
    sudo systemctl enable gist-worker.timer
    sudo systemctl start gist-worker.timer

Usage:
    gist-worker.py --check-once           # Single poll cycle
    gist-worker.py --install-service      # Install systemd timer
    gist-worker.py --status               # Show worker status
"""
import json, os, sys, argparse, subprocess, tempfile, time, traceback
from pathlib import Path
from datetime import datetime

# ─── CONFIGURATION ──────────────────────────────────────────────────
GIST_ID = os.environ.get("GIST_WORKER_GIST_ID", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
NODE_ID = os.environ.get("GIST_WORKER_NODE", "")
POLL_INTERVAL = int(os.environ.get("GIST_WORKER_INTERVAL", "30"))

TASK_DIR = Path("/srv/gist-tasks")
LOG_FILE = Path("/var/log/gist-worker.log")
LOCK_FILE = Path("/tmp/gist-worker.lock")

GIST_API = "https://api.github.com"
GIST_RAW = f"https://gist.githubusercontent.com/carlosfrias/{GIST_ID}/raw"


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except PermissionError:
        pass


def ensure_dirs():
    for d in [TASK_DIR / "pending", TASK_DIR / "running", TASK_DIR / "completed", TASK_DIR / "results"]:
        d.mkdir(parents=True, exist_ok=True)


def acquire_lock() -> bool:
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            if os.path.exists(f"/proc/{pid}"):
                return False
        except ValueError:
            pass
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def release_lock():
    try:
        LOCK_FILE.unlink()
    except FileNotFoundError:
        pass


def gist_api(method: str, path: str, data=None) -> dict:
    """Call GitHub Gist API."""
    import urllib.request
    url = f"{GIST_API}/gists/{GIST_ID}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def fetch_gist_file(filename: str) -> str:
    """Fetch a file from the Gist via raw URL."""
    import urllib.request
    url = f"{GIST_RAW}/{filename}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        return ""


def post_gist_file(filename: str, content: str) -> bool:
    """Post or update a file in the Gist."""
    if not GITHUB_TOKEN:
        log("⚠ No GITHUB_TOKEN — cannot post results")
        return False

    result = gist_api("PATCH", "", {"files": {filename: {"content": content}}})
    if "error" in result:
        log(f"✗ Failed to post {filename}: {result['error']}")
        return False
    log(f"✓ Posted {filename} to Gist")
    return True


def check_for_tasks() -> list:
    """Check Gist for tasks addressed to this node."""
    tasks = []
    # Look for files matching pattern: tasks-<node>-<id>.json
    gist_data = gist_api("GET", "")
    if "error" in gist_data:
        log(f"✗ Failed to fetch Gist: {gist_data['error']}")
        return tasks

    files = gist_data.get("files", {})
    for fname, fmeta in files.items():
        if not fname.startswith("task-"):
            continue
        parts = fname.replace(".json", "").split("-")
        if len(parts) < 4:
            continue
        target_node = parts[1]
        if target_node != NODE_ID and target_node != "all":
            continue
        task_id = "-".join(parts[2:])
        raw = fetch_gist_file(fname)
        if not raw:
            continue
        try:
            task = json.loads(raw)
            task["_gist_file"] = fname
            task["_task_id"] = task_id
            tasks.append(task)
        except json.JSONDecodeError:
            log(f"⚠ Malformed task JSON: {fname}")
            continue

    return tasks


def execute_task(task: dict) -> dict:
    """Execute a task and return result dict."""
    command = task.get("command", "")
    task_type = task.get("type", "shell")
    task_id = task.get("_task_id", "unknown")

    start = time.time()
    log(f"▶ Executing task {task_id} ({task_type})")

    if task_type == "shell":
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=task.get("timeout", 300),
            )
            return {
                "task_id": task_id,
                "node": NODE_ID,
                "status": "success" if result.returncode == 0 else "failed",
                "rc": result.returncode,
                "stdout": result.stdout[:5000],
                "stderr": result.stderr[:2000],
                "elapsed_seconds": round(time.time() - start, 2),
                "completed_at": datetime.now().isoformat(),
            }
        except subprocess.TimeoutExpired:
            return {
                "task_id": task_id,
                "node": NODE_ID,
                "status": "timeout",
                "rc": -1,
                "stdout": "",
                "stderr": f"Timeout after {task.get('timeout', 300)}s",
                "elapsed_seconds": task.get("timeout", 300),
                "completed_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "node": NODE_ID,
                "status": "error",
                "rc": -1,
                "stdout": "",
                "stderr": traceback.format_exc(),
                "elapsed_seconds": round(time.time() - start, 2),
                "completed_at": datetime.now().isoformat(),
            }
    elif task_type == "ollama":
        model = task.get("model", "qwen3:8b")
        prompt = task.get("prompt", "")
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=task.get("timeout", 300),
            )
            return {
                "task_id": task_id,
                "node": NODE_ID,
                "status": "success" if result.returncode == 0 else "failed",
                "rc": result.returncode,
                "stdout": result.stdout[:10000],
                "stderr": result.stderr[:2000],
                "model": model,
                "elapsed_seconds": round(time.time() - start, 2),
                "completed_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "node": NODE_ID,
                "status": "error",
                "rc": -1,
                "stdout": "",
                "stderr": str(e),
                "elapsed_seconds": round(time.time() - start, 2),
                "completed_at": datetime.now().isoformat(),
            }
    else:
        return {
            "task_id": task_id,
            "node": NODE_ID,
            "status": "unsupported_type",
            "rc": -1,
            "stderr": f"Unknown task type: {task_type}",
            "completed_at": datetime.now().isoformat(),
        }


def mark_task_completed(task: dict, result: dict) -> bool:
    """Post result to Gist and clean up."""
    task_id = task.get("_task_id", "unknown")
    result_fname = f"result-{NODE_ID}-{task_id}.json"
    content = json.dumps(result, indent=2)
    return post_gist_file(result_fname, content)


def poll_once():
    """Single poll cycle."""
    if not GIST_ID:
        log("✗ GIST_WORKER_GIST_ID not set")
        return
    if not NODE_ID:
        log("✗ GIST_WORKER_NODE not set")
        return

    if not acquire_lock():
        log("⚠ Another worker instance is running")
        return

    try:
        ensure_dirs()
        tasks = check_for_tasks()
        if not tasks:
            log("○ No tasks for this node")
            return

        for task in tasks:
            result = execute_task(task)
            if result.get("status") in ("success", "failed", "timeout", "error"):
                mark_task_completed(task, result)
    finally:
        release_lock()


def install_service():
    """Install systemd service and timer."""
    service_content = f"""[Unit]
Description=Gist Message Queue Worker — autonomously polls GitHub Gist for tasks
After=network.target

[Service]
Type=oneshot
Environment="GIST_WORKER_GIST_ID={GIST_ID}"
Environment="GIST_WORKER_NODE=%i"
Environment="GITHUB_TOKEN={GITHUB_TOKEN}"
Environment="GIST_WORKER_INTERVAL={POLL_INTERVAL}"
ExecStart=/usr/local/bin/gist-worker.py --check-once
User=pi-worker
StandardOutput=journal
StandardError=journal
"""

    timer_content = f"""[Unit]
Description=Gist Worker Timer — poll every {POLL_INTERVAL}s

[Timer]
OnBootSec=60
OnUnitActiveSec={POLL_INTERVAL}s
AccuracySec=5s
Persistent=true

[Install]
WantedBy=timers.target
"""

    print("=== Systemd Service ===")
    print(service_content)
    print("=== Systemd Timer ===")
    print(timer_content)
    print()
    print("To install:")
    print("  sudo tee /etc/systemd/system/gist-worker@.service << 'EOF'")
    print(service_content)
    print("  EOF")
    print("  sudo tee /etc/systemd/system/gist-worker.timer << 'EOF'")
    print(timer_content)
    print("  EOF")
    print("  sudo systemctl daemon-reload")
    print(f"  sudo systemctl enable gist-worker@{NODE_ID or 'fnet3'}.timer")
    print(f"  sudo systemctl start gist-worker@{NODE_ID or 'fnet3'}.timer")
    print("  sudo systemctl status gist-worker.timer")


def show_status():
    """Show worker status."""
    print(f"Gist Worker Status")
    print(f"  Gist ID: {GIST_ID or '(not set)'}")
    print(f"  Node: {NODE_ID or '(not set)'}")
    print(f"  Poll interval: {POLL_INTERVAL}s")
    print(f"  Log: {LOG_FILE}")
    print(f"  Lock: {LOCK_FILE} (exists={LOCK_FILE.exists()})")
    print(f"  Task dir: {TASK_DIR}")
    print(f"  GitHub token: {'✓ set' if GITHUB_TOKEN else '✗ not set'}")
    print()
    print("Recent log entries:")
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text().strip().split("\n")[-10:]
        for line in lines:
            print(f"  {line}")
    else:
        print("  (no log yet)")


def main():
    parser = argparse.ArgumentParser(description="Gist autonomous worker")
    parser.add_argument("--check-once", action="store_true", help="Single poll cycle")
    parser.add_argument("--install-service", action="store_true", help="Print systemd unit files")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--gist-id", default=GIST_ID, help="GitHub Gist ID")
    parser.add_argument("--node", default=NODE_ID, help="Node identifier")
    parser.add_argument("--token", default=GITHUB_TOKEN, help="GitHub personal access token")
    parser.add_argument("--interval", type=int, default=POLL_INTERVAL, help="Poll interval in seconds")
    args = parser.parse_args()

    # Use local vars to avoid shadowing globals
    gist_id = args.gist_id or GIST_ID
    node_id = args.node or NODE_ID
    github_token = args.token or GITHUB_TOKEN
    poll_interval = args.interval or POLL_INTERVAL

    if args.status:
        show_status()
    elif args.install_service:
        install_service()
    elif args.check_once:
        poll_once()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
