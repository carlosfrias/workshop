#!/usr/bin/env python3
"""
decompose-watcher.py — Automatic decomposition trigger processor
Part of TI-023: Auto-decompose + node dispatch pipeline

Scans ~/.pi/decomposition-triggers/pending/ for classification triggers,
invokes the decomposer, then dispatches sub-tasks to lab nodes.

Usage:
    python3 decompose-watcher.py --daemon          # Run continuously
    python3 decompose-watcher.py --once            # Single poll cycle
    python3 decompose-watcher.py --status          # Show pending/completed triggers
    python3 decompose-watcher.py --dry-run         # Process without actual dispatch

Systemd:
    systemctl --user enable decompose-watcher.timer
    systemctl --user start decompose-watcher.timer
"""
import json
import os
import sys
import argparse
import subprocess
import time
import traceback
from pathlib import Path
from datetime import datetime

# ── Performance Logging ────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
try:
    from performance_logger import log_decomposition, log_dispatch
except ImportError:
    log_decomposition = None
    log_dispatch = None

# ── PATHS ──────────────────────────────────────────────────────────
TRIGGER_DIR = Path.home() / ".pi" / "decomposition-triggers"
PENDING_DIR = TRIGGER_DIR / "pending"
COMPLETED_DIR = TRIGGER_DIR / "completed"
FAILED_DIR = TRIGGER_DIR / "failed"
PLAN_DIR = TRIGGER_DIR / "plans"

SCRIPTS_DIR = Path(__file__).parent
TI011_DIR = SCRIPTS_DIR  # Same directory

# ── CONFIG ─────────────────────────────────────────────────────────
POLL_INTERVAL = 5  # seconds in daemon mode
MAX_DECOMPOSE_TIME = 120  # seconds before killing decomposer
MAX_SUBTASKS = 10  # safety cap per decomposition

# ── UTILS ──────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def ensure_dirs():
    for d in [PENDING_DIR, COMPLETED_DIR, FAILED_DIR, PLAN_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_trigger(path: Path) -> dict:
    return json.loads(path.read_text())


def move_trigger(src: Path, dest_dir: Path, status: str):
    dest = dest_dir / src.name
    data = load_trigger(src)
    data["status"] = status
    data["processed_at"] = datetime.now().isoformat()
    dest.write_text(json.dumps(data, indent=2))
    src.unlink()
    return dest


# ── DECOMPOSITION ──────────────────────────────────────────────────

def decompose(trigger: dict, dry_run: bool = False) -> dict:
    """Invoke decompose_llm.py to break trigger prompt into sub-tasks."""
    
    prompt = trigger["prompt"]
    complexity = trigger["complexity"]
    start_time = time.time()
    
    # If trigger already has sub_tasks (test injection or pre-decomposed), use them directly
    trigger_subtasks = trigger.get("sub_tasks", [])
    if trigger_subtasks and not dry_run:
        log(f"  Using pre-populated sub-tasks from trigger ({len(trigger_subtasks)} tasks)")
        latency_ms = int((time.time() - start_time) * 1000)
        if log_decomposition:
            log_decomposition(
                trigger_id=trigger.get("id", "unknown"),
                prompt=prompt,
                sub_task_count=len(trigger_subtasks),
                latency_ms=latency_ms,
                model_used="pre-populated",
                provider="local",
                success=True,
            )
        return {
            "success": True,
            "plan": trigger,
            "subtasks": trigger_subtasks,
            "latency_ms": latency_ms,
        }
    
    # Map complexity to decompose_llm.py tier (numeric: 0, 1, 2)
    tier_map = {"MEDIUM": "1", "HARD": "2"}
    tier = tier_map.get(complexity, "0")
    
    decompose_script = TI011_DIR / "decompose_llm.py"
    if not decompose_script.exists():
        return {
            "success": False,
            "error": f"decompose_llm.py not found at {decompose_script}",
            "subtasks": [],
        }
    
    if dry_run:
        log(f"[DRY-RUN] Would decompose: {prompt[:60]}...")
        # If trigger already has sub_tasks (test injection), use them
        trigger_subtasks = trigger.get("sub_tasks", [])
        return {
            "success": True,
            "dry_run": True,
            "subtasks": trigger_subtasks if trigger_subtasks else [
                {"id": "dry-1", "description": "Example sub-task 1", "model": "qwen3:8b", "node": "fnet3"},
                {"id": "dry-2", "description": "Example sub-task 2", "model": "gemma4:e4b", "node": "fnet4"},
            ],
        }
    
    # Run decomposer
    try:
        cmd = [
            "python3", str(decompose_script),
            "--prompt", prompt,
            "--tier", tier,
            "--json",
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=MAX_DECOMPOSE_TIME,
        )
        
        if proc.returncode != 0:
            latency_ms = int((time.time() - start_time) * 1000)
            if log_decomposition:
                log_decomposition(
                    trigger_id=trigger.get("id", "unknown"),
                    prompt=prompt,
                    sub_task_count=0,
                    latency_ms=latency_ms,
                    model_used="decompose_llm.py",
                    provider="local",
                    success=False,
                    error=f"exited {proc.returncode}",
                )
            return {
                "success": False,
                "error": f"decompose_llm.py exited {proc.returncode}: {proc.stderr[:200]}",
                "subtasks": [],
                "latency_ms": latency_ms,
            }
        
        result = json.loads(proc.stdout)
        
        # Normalize: decompose_llm.py uses "sub_tasks", we use "subtasks"
        subtasks = result.get("sub_tasks", []) or result.get("subtasks", [])
        
        # Check for decomposer errors
        if result.get("error"):
            latency_ms = int((time.time() - start_time) * 1000)
            if log_decomposition:
                log_decomposition(
                    trigger_id=trigger.get("id", "unknown"),
                    prompt=prompt,
                    sub_task_count=0,
                    latency_ms=latency_ms,
                    model_used="decompose_llm.py",
                    provider="local",
                    success=False,
                    error=result['error'],
                )
            return {
                "success": False,
                "error": f"Decomposer error: {result['error']}",
                "subtasks": [],
                "latency_ms": latency_ms,
            }
        
        latency_ms = int((time.time() - start_time) * 1000)
        if log_decomposition:
            log_decomposition(
                trigger_id=trigger.get("id", "unknown"),
                prompt=prompt,
                sub_task_count=len(subtasks),
                latency_ms=latency_ms,
                model_used="decompose_llm.py",
                provider="local",
                success=True,
            )
        return {
            "success": True,
            "plan": result,
            "subtasks": subtasks,
            "latency_ms": latency_ms,
        }
    
    except subprocess.TimeoutExpired:
        latency_ms = int((time.time() - start_time) * 1000)
        if log_decomposition:
            log_decomposition(
                trigger_id=trigger.get("id", "unknown"),
                prompt=prompt,
                sub_task_count=0,
                latency_ms=latency_ms,
                model_used="decompose_llm.py",
                provider="local",
                success=False,
                error=f"timed out after {MAX_DECOMPOSE_TIME}s",
            )
        return {
            "success": False,
            "error": f"Decomposition timed out after {MAX_DECOMPOSE_TIME}s",
            "subtasks": [],
            "latency_ms": latency_ms,
        }
    except json.JSONDecodeError as e:
        latency_ms = int((time.time() - start_time) * 1000)
        if log_decomposition:
            log_decomposition(
                trigger_id=trigger.get("id", "unknown"),
                prompt=prompt,
                sub_task_count=0,
                latency_ms=latency_ms,
                model_used="decompose_llm.py",
                provider="local",
                success=False,
                error=f"invalid JSON: {e}",
            )
        return {
            "success": False,
            "error": f"Invalid JSON from decomposer: {e}",
            "subtasks": [],
            "latency_ms": latency_ms,
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        if log_decomposition:
            log_decomposition(
                trigger_id=trigger.get("id", "unknown"),
                prompt=prompt,
                sub_task_count=0,
                latency_ms=latency_ms,
                model_used="decompose_llm.py",
                provider="local",
                success=False,
                error=str(e)[:100],
            )
        return {
            "success": False,
            "error": f"Decomposition failed: {str(e)[:100]}",
            "subtasks": [],
            "latency_ms": latency_ms,
        }


# ── NODE DISPATCH (P4) ─────────────────────────────────────────────

def dispatch_subtasks(subtasks: list, dry_run: bool = False, trigger_id: str = "unknown") -> dict:
    """Dispatch sub-tasks to lab nodes via submit_task.py."""
    
    submit_script = TI011_DIR / "submit_task.py"
    if not submit_script.exists():
        return {
            "dispatched": 0,
            "errors": [f"submit_task.py not found at {submit_script}"],
        }
    
    results = []
    errors = []
    
    for i, subtask in enumerate(subtasks[:MAX_SUBTASKS]):
        task_id = subtask.get("id", f"subtask-{i}")
        task_text = subtask.get("description", "")  # decompose_llm.py uses "description"
        target_node = subtask.get("node", "")
        
        # Use NodeRegistry to find best node if not specified
        if not target_node or target_node == "auto":
            try:
                from ti011_node_registry import NodeRegistry
                reg = NodeRegistry()
                route = reg.best_model_for(subtask.get("complexity", "medium"))
                target_node = route.get("node", "fnet3")
            except Exception:
                target_node = "fnet3"
        
        if dry_run:
            log(f"[DRY-RUN] Would dispatch task {task_id} to {target_node}")
            results.append({
                "task_id": task_id,
                "node": target_node,
                "status": "dry_run",
            })
            continue
        
        # Write task to temp file (submit_task.py uses --file)
        task_json = {
            "id": task_id,
            "type": "shell",
            "command": task_text,
            "timeout": 300,
        }
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(task_json, f)
            task_file = f.name
        
        try:
            cmd = [
                "python3", str(submit_script),
                "--node", target_node,
                "--file", task_file,
            ]
            dispatch_start = time.time()
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            dispatch_latency_ms = int((time.time() - dispatch_start) * 1000)
            os.unlink(task_file)
            
            if proc.returncode == 0:
                results.append({
                    "task_id": task_id,
                    "node": target_node,
                    "status": "submitted",
                    "latency_ms": dispatch_latency_ms,
                })
                if log_dispatch:
                    log_dispatch(
                        trigger_id=trigger_id,
                        sub_task_id=task_id,
                        node=target_node,
                        model=subtask.get("model", "unknown"),
                        latency_ms=dispatch_latency_ms,
                        success=True,
                        provider="local",
                    )
            else:
                errors.append(f"Task {task_id} failed: {proc.stderr[:100]}")
                if log_dispatch:
                    log_dispatch(
                        trigger_id=trigger_id,
                        sub_task_id=task_id,
                        node=target_node,
                        model=subtask.get("model", "unknown"),
                        latency_ms=dispatch_latency_ms,
                        success=False,
                        error=proc.stderr[:100],
                        provider="local",
                    )
        
        except Exception as e:
            try:
                os.unlink(task_file)
            except:
                pass
            errors.append(f"Task {task_id} exception: {str(e)[:60]}")
            if log_dispatch:
                log_dispatch(
                    trigger_id=trigger_id,
                    sub_task_id=task_id,
                    node=target_node,
                    model=subtask.get("model", "unknown"),
                    latency_ms=0,
                    success=False,
                    error=str(e)[:60],
                    provider="local",
                )
    
    return {
        "dispatched": len(results),
        "errors": errors,
        "results": results,
    }


# ── MAIN PROCESSOR ─────────────────────────────────────────────────

def process_triggers(dry_run: bool = False) -> dict:
    """Process all pending triggers."""
    ensure_dirs()
    
    pending = sorted(PENDING_DIR.glob("*.json"))
    if not pending:
        return {"processed": 0, "message": "No pending triggers"}
    
    log(f"Processing {len(pending)} pending trigger(s)...")
    
    stats = {"processed": 0, "decomposed": 0, "dispatched": 0, "failed": 0, "errors": []}
    
    for trigger_path in pending:
        try:
            trigger = load_trigger(trigger_path)
            trigger_id = trigger.get("id", trigger_path.stem)
            
            log(f"Trigger {trigger_id}: {trigger['prompt'][:50]}...")
            
            # Step 1: Decompose
            decomp = decompose(trigger, dry_run)
            
            if not decomp["success"]:
                log(f"  ❌ Decomposition failed: {decomp['error']}")
                move_trigger(trigger_path, FAILED_DIR, "decompose_failed")
                stats["failed"] += 1
                stats["errors"].append(f"{trigger_id}: {decomp['error']}")
                continue
            
            log(f"  ✅ Decomposed into {len(decomp.get('subtasks', []))} sub-tasks")
            stats["decomposed"] += 1
            
            # Save plan
            plan_file = PLAN_DIR / f"{trigger_id}.json"
            plan_file.write_text(json.dumps(decomp, indent=2))
            
            # Step 2: Dispatch sub-tasks
            dispatch = dispatch_subtasks(decomp.get("subtasks", []), dry_run, trigger_id=trigger_id)
            
            if dispatch["errors"]:
                for err in dispatch["errors"]:
                    log(f"  ⚠️  Dispatch error: {err}")
                    stats["errors"].append(err)
            
            log(f"  ✅ Dispatched {dispatch['dispatched']} sub-tasks")
            stats["dispatched"] += dispatch["dispatched"]
            
            # Mark completed
            completed_path = move_trigger(trigger_path, COMPLETED_DIR, "completed")
            trigger = load_trigger(completed_path)
            trigger["plan_file"] = str(plan_file)
            trigger["dispatch_result"] = dispatch
            completed_path.write_text(json.dumps(trigger, indent=2))
            
            stats["processed"] += 1
        
        except Exception as e:
            log(f"  ❌ Unexpected error processing {trigger_path.name}: {e}")
            stats["failed"] += 1
            stats["errors"].append(f"{trigger_path.name}: {str(e)[:60]}")
            traceback.print_exc()
    
    log(f"Done: {stats['processed']} processed, {stats['decomposed']} decomposed, {stats['dispatched']} dispatched, {stats['failed']} failed")
    return stats


def show_status():
    """Show trigger queue status."""
    ensure_dirs()
    
    pending = list(PENDING_DIR.glob("*.json"))
    completed = list(COMPLETED_DIR.glob("*.json"))
    failed = list(FAILED_DIR.glob("*.json"))
    plans = list(PLAN_DIR.glob("*.json"))
    
    print(f"Decomposition Trigger Status")
    print(f"  Pending:   {len(pending)}")
    print(f"  Completed: {len(completed)}")
    print(f"  Failed:    {len(failed)}")
    print(f"  Plans:     {len(plans)}")
    
    if pending:
        print(f"\nPending triggers:")
        for p in pending:
            t = load_trigger(p)
            print(f"  - {t['id']}: {t['prompt'][:50]}... (complexity: {t['complexity']})")
    
    if failed:
        print(f"\nFailed triggers:")
        for f in failed:
            t = load_trigger(f)
            print(f"  - {t['id']}: status={t.get('status', 'unknown')}")


def run_daemon():
    """Continuous polling mode."""
    log("Decompose watcher daemon started")
    log(f"Polling every {POLL_INTERVAL}s")
    log("Press Ctrl+C to stop")
    
    try:
        while True:
            stats = process_triggers()
            if stats["processed"] > 0:
                log(f"Cycle complete. Sleeping {POLL_INTERVAL}s...")
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log("Daemon stopped")


# ── CLI ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Auto-decomposition watcher")
    parser.add_argument("--daemon", action="store_true", help="Run continuous polling")
    parser.add_argument("--once", action="store_true", help="Single poll cycle")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--dry-run", action="store_true", help="Process without actual dispatch")
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.daemon:
        run_daemon()
    elif args.once:
        process_triggers(dry_run=args.dry_run)
    else:
        # Default: single cycle with dry-run if no flags
        process_triggers(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
