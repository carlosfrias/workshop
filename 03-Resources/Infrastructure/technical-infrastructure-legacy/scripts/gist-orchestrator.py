#!/usr/bin/env python3
"""
gist-orchestrator.py — Orchestrator-side Gist task dispatcher + result collector
Part of TI-011 meta-orchestration (off-premise remote access)

Dispatches tasks to lab nodes via GitHub Gist, collects results asynchronously.
Works through firewalls — only needs HTTPS.

Usage:
    # Submit task to a specific node
    gist-orchestrator.py --submit --node fnet3 --command "ollama list"

    # Submit task to all nodes
    gist-orchestrator.py --submit-all --command "ollama list"

    # Collect results
    gist-orchestrator.py --collect --since 300

    # Show status of all nodes
    gist-orchestrator.py --status

Environment:
    GIST_ORCHESTRATOR_GIST_ID — Gist ID for the shared task queue
    GITHUB_TOKEN — Personal access token (needs gist scope)
"""
import json, os, sys, argparse, time
from pathlib import Path
from datetime import datetime, timedelta

GIST_ID = os.environ.get("GIST_ORCHESTRATOR_GIST_ID", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GIST_API = "https://api.github.com"
GIST_RAW = f"https://gist.githubusercontent.com/carlosfrias/{GIST_ID}/raw"

NODES = [f"fnet{i}" for i in range(1, 8)]


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def gist_api(method: str, path: str, data=None) -> dict:
    import urllib.request
    url = f"{GIST_API}/gists/{GIST_ID}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    req_data = json.dumps(data).encode("utf-8") if data else None
    if req_data:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def submit_task(node: str, command: str, task_type: str = "shell", timeout: int = 300) -> str:
    """Submit a task to the Gist for a specific node."""
    if not GIST_ID or not GITHUB_TOKEN:
        log("✗ GIST_ORCHESTRATOR_GIST_ID and GITHUB_TOKEN required")
        return ""

    task_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{os.urandom(2).hex()}"
    task = {
        "id": task_id,
        "node": node,
        "type": task_type,
        "command": command,
        "timeout": timeout,
        "submitted_at": datetime.now().isoformat(),
    }

    fname = f"task-{node}-{task_id}.json"
    result = gist_api("PATCH", "", {"files": {fname: {"content": json.dumps(task, indent=2)}}})

    if "error" in result:
        log(f"✗ Failed to submit: {result['error']}")
        return ""

    log(f"✓ Submitted task {task_id} to {node}")
    log(f"  Gist: https://gist.github.com/carlosfrias/{GIST_ID}")
    return task_id


def collect_results(since_seconds: int = 300) -> list:
    """Collect all results from the Gist newer than since_seconds."""
    if not GIST_ID:
        log("✗ GIST_ORCHESTRATOR_GIST_ID required")
        return []

    cutoff = datetime.now() - timedelta(seconds=since_seconds)
    log(f"Collecting results since {cutoff.strftime('%H:%M:%S')}...")

    gist_data = gist_api("GET", "")
    if "error" in gist_data:
        log(f"✗ Failed: {gist_data['error']}")
        return []

    results = []
    files = gist_data.get("files", {})
    for fname, fmeta in files.items():
        if not fname.startswith("result-"):
            continue
        # Check age from fmeta
        updated = fmeta.get("updated_at", "")
        if updated:
            try:
                updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                if updated_dt < cutoff:
                    continue
            except ValueError:
                pass

        # Fetch content
        import urllib.request
        url = fmeta.get("raw_url", "")
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                content = resp.read().decode("utf-8")
                results.append(json.loads(content))
        except Exception:
            continue

    log(f"Collected {len(results)} result(s)")
    return results


def show_status():
    """Show status of all nodes from Gist."""
    if not GIST_ID:
        log("✗ GIST_ORCHESTRATOR_GIST_ID required")
        return

    log(f"Gist Task Queue: https://gist.github.com/carlosfrias/{GIST_ID}")
    log("")

    gist_data = gist_api("GET", "")
    if "error" in gist_data:
        log(f"✗ {gist_data['error']}")
        return

    files = gist_data.get("files", {})
    pending = [f for f in files if f.startswith("task-")]
    completed = [f for f in files if f.startswith("result-")]

    log(f"Pending tasks: {len(pending)}")
    for f in sorted(pending):
        parts = f.replace(".json", "").split("-")
        if len(parts) >= 3:
            node = parts[1]
            tid = "-".join(parts[2:])
            log(f"  ⏳ {node}/{tid[:12]}")

    log("")
    log(f"Completed results: {len(completed)}")
    for f in sorted(completed, reverse=True)[:10]:
        parts = f.replace(".json", "").split("-")
        if len(parts) >= 3:
            node = parts[1]
            tid = "-".join(parts[2:])
            log(f"  ✅ {node}/{tid[:12]}")


def main():
    parser = argparse.ArgumentParser(description="Gist orchestrator")
    parser.add_argument("--gist-id", default=GIST_ID, help="GitHub Gist ID")
    parser.add_argument("--token", default=GITHUB_TOKEN, help="GitHub PAT")
    parser.add_argument("--submit", action="store_true", help="Submit task to a node")
    parser.add_argument("--submit-all", action="store_true", help="Submit to all nodes")
    parser.add_argument("--node", default="", help="Target node")
    parser.add_argument("--command", default="", help="Shell command")
    parser.add_argument("--type", default="shell", help="Task type (shell, ollama)")
    parser.add_argument("--collect", action="store_true", help="Collect results")
    parser.add_argument("--since", type=int, default=300, help="Collect since N seconds ago")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--watch", action="store_true", help="Watch for results")
    parser.add_argument("--poll-interval", type=int, default=10, help="Poll interval in seconds")
    args = parser.parse_args()

    GIST_ID = args.gist_id or GIST_ID
    GITHUB_TOKEN = args.token or GITHUB_TOKEN

    if not GIST_ID:
        log("✗ Set GIST_ORCHESTRATOR_GIST_ID or use --gist-id")
        sys.exit(1)

    if args.status:
        show_status()
    elif args.submit:
        if not args.node or not args.command:
            log("✗ --submit requires --node and --command")
            sys.exit(1)
        submit_task(args.node, args.command, args.type)
    elif args.submit_all:
        if not args.command:
            log("✗ --submit-all requires --command")
            sys.exit(1)
        for node in NODES:
            submit_task(node, args.command, args.type)
            time.sleep(1)
    elif args.collect:
        results = collect_results(args.since)
        for r in results:
            status_icon = "✅" if r.get("status") == "success" else "❌"
            log(f"{status_icon} {r.get('node', '?')}/{r.get('task_id', '?')[:8]}: {r.get('status', '?')} ({r.get('elapsed_seconds', 0)}s)")
            if r.get("stdout"):
                for line in r["stdout"].split("\n")[:5]:
                    log(f"    {line}")
    elif args.watch:
        log(f"Watching Gist {GIST_ID} for results (Ctrl+C to stop)...")
        seen = set()
        while True:
            try:
                results = collect_results(since_seconds=args.poll_interval + 5)
                for r in results:
                    key = f"{r.get('node')}-{r.get('task_id')}"
                    if key not in seen:
                        seen.add(key)
                        status_icon = "✅" if r.get("status") == "success" else "❌"
                        log(f"{status_icon} NEW: {r.get('node', '?')}/{r.get('task_id', '?')[:8]}")
                time.sleep(args.poll_interval)
            except KeyboardInterrupt:
                log("Stopped")
                break
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
