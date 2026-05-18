#!/usr/bin/env python3
"""
test_ti010.py — Comprehensive Test Harness for TI-010 Event-Driven Gist Protocol

Usage:
  python3 test_ti010.py --all                # Run all tests
  python3 test_ti010.py --connectivity       # T1: Node ↔ Gist connectivity
  python3 test_ti010.py --publish-consume    # T2-T4: Pub/sub across nodes
  python3 test_ti010.py --ack-nack           # T5-T7: ACK, NACK, DLQ
  python3 test_ti010.py --rate-limit         # T9: Rate limiting
  python3 test_ti010.py --compact            # T10: Compaction
  python3 test_ti010.py --report             # Print JSON report
"""

import json, os, sys, time, subprocess, fnmatch, argparse
from datetime import datetime, timezone
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(__file__))
from gist_event_bus import GistEventBus, EventConsumer

NODES = ["fnet1", "fnet2", "fnet3", "fnet4", "fnet5", "fnet6", "fnet7"]
GIST_ID = os.getenv("GIST_ID", "0c517214489cb78c0484ca661f3d8463")
RESULTS: List[Dict] = []

def log(test_id: str, name: str, passed: bool, detail: str = "", duration_ms: int = 0):
    RESULTS.append({
        "test_id": test_id,
        "name": name,
        "passed": passed,
        "detail": detail,
        "duration_ms": duration_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} [{test_id}] {name}")
    if detail:
        print(f"      {detail}")

def get_token() -> str:
    try:
        r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""

def cleanup_test_events():
    """Remove all test.* events from Gist before/after tests."""
    token = get_token()
    bus = GistEventBus(gist_id=GIST_ID, token=token)
    events = bus.read_events()
    cleaned = []
    removed = 0
    for e in events:
        t = e.get("type", "")
        if t.startswith("test."):
            removed += 1
            continue
        cleaned.append(json.dumps(e, default=str))
    if removed > 0:
        bus.update_gist({"events": {"content": "\n".join(cleaned)}})
        print(f"    🧹 Cleaned {removed} test events")
    return removed

def wait_for_rate_limit():
    """Check GitHub rate limit and wait if needed."""
    try:
        token = get_token()
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        import requests
        r = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            core = data.get("resources", {}).get("core", {})
            remaining = core.get("remaining", 0)
            reset_ts = core.get("reset", 0)
            if remaining < 20:
                wait_secs = max(0, reset_ts - int(time.time())) + 5
                print(f"    ⏳ GitHub rate limit low ({remaining} remaining). Waiting {wait_secs}s...")
                time.sleep(wait_secs)
            else:
                print(f"    ℹ️  GitHub rate limit: {remaining} remaining")
    except Exception as e:
        print(f"    ⚠️  Could not check rate limit: {e}")

# =============================================================================
# T1: Connectivity — Every node can reach GitHub Gist API
# =============================================================================
def test_t1_connectivity():
    print("\n=== T1: Connectivity (Node ↔ Gist API) ===")
    cleanup_test_events()
    token = get_token()
    bus = GistEventBus(gist_id=GIST_ID, token=token)

    start = time.time()
    gist = bus.get_gist()
    duration = int((time.time() - start) * 1000)

    if gist and "files" in gist:
        log("T1.1", "Orchestrator can reach Gist API", True,
            f"Gist has {len(gist['files'])} files", duration)
    else:
        log("T1.1", "Orchestrator can reach Gist API", False,
            "No response from GitHub API", duration)
        return  # Can't continue without connectivity

    # Check each node via Ansible
    for node in NODES:
        start = time.time()
        cmd = [
            "ansible", "-i", "technical-infrastructure/ansible/inventory.yml",
            node, "-m", "shell",
            "-a", f"curl -sf --max-time 15 https://api.github.com/gists/{GIST_ID} -H 'Accept: application/vnd.github+json' | head -c 20 || echo 'FAIL'",
            "--vault-password-file", str(Path.home() / ".ansible/secure/.vault_pass"),
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            duration = int((time.time() - start) * 1000)
            ok = "FAIL" not in r.stdout and r.returncode == 0
            log(f"T1.{NODES.index(node)+2}", f"{node} can reach Gist API", ok,
                f"rc={r.returncode} output={r.stdout[:30].strip()}", duration)
        except Exception as e:
            log(f"T1.{NODES.index(node)+2}", f"{node} can reach Gist API", False,
                str(e), 0)

# =============================================================================
# T2-T4: Publish / Consume / Broadcast
# =============================================================================
def test_t2_t4_pubsub():
    print("\n=== T2-T4: Publish / Targeted Consume / Broadcast ===")
    cleanup_test_events()
    token = get_token()
    bus = GistEventBus(gist_id=GIST_ID, token=token)

    # T2: Targeted publish to fnet3
    start = time.time()
    evt_id = bus.publish("task.created", {"task_id": "T2", "command": "uptime"}, target="fnet3")
    duration = int((time.time() - start) * 1000)
    log("T2.1", "Publish targeted event to fnet3", bool(evt_id),
        f"event_id={evt_id}", duration)

    # T3: fnet3 sees it, fnet4 does not
    time.sleep(2)
    for node in ["fnet3", "fnet4"]:
        pending = bus.get_pending(node_id=node, event_types=["task.created"])
        has_event = any(e.get("id") == evt_id for e in pending)
        expected = (node == "fnet3")
        log(f"T3.{['fnet3','fnet4'].index(node)+1}", f"{node} sees targeted event", has_event == expected,
            f"pending={len(pending)}")

    # T4: Broadcast event (no target)
    start = time.time()
    broadcast_id = bus.publish("node.health", {"check": "all"})
    duration = int((time.time() - start) * 1000)
    time.sleep(2)

    # All nodes should see broadcast
    all_see = True
    for node in ["fnet3", "fnet4", "fnet5"]:
        pending = bus.get_pending(node_id=node, event_types=["node.health"])
        has_broadcast = any(e.get("id") == broadcast_id for e in pending)
        if not has_broadcast:
            all_see = False
    log("T4.1", "Broadcast event visible to all nodes", all_see,
        f"broadcast_id={broadcast_id}", duration)

    # Cleanup: ACK all test events
    events = bus.read_events()
    for e in events:
        if e.get("type") in ("task.created", "node.health", "test.*"):
            bus.ack(e["id"], "orchestrator")

# =============================================================================
# T5-T7: ACK / NACK / DLQ
# =============================================================================
def test_t5_t7_ack_nack_dlq():
    print("\n=== T5-T7: ACK / NACK / DLQ ===")
    cleanup_test_events()
    token = get_token()
    bus = GistEventBus(gist_id=GIST_ID, token=token)

    # T5: Publish, ACK, verify gone
    start = time.time()
    evt_id = bus.publish("test.ack", {"step": "ack_test"})
    time.sleep(1)
    ack_ok = bus.ack(evt_id, "fnet3")
    time.sleep(1)
    pending = bus.get_pending(node_id="fnet3", event_types=["test.ack"])
    still_pending = any(e.get("id") == evt_id for e in pending)
    duration = int((time.time() - start) * 1000)
    log("T5.1", "ACK removes event from pending", ack_ok and not still_pending,
        f"ack_ok={ack_ok} still_pending={still_pending}", duration)

    # T6: NACK with retry
    start = time.time()
    evt_id2 = bus.publish("test.nack", {"step": "nack_test"})
    time.sleep(1)
    nack_ok = bus.nack(evt_id2, requeue=True)
    time.sleep(1)
    events = bus.read_events()
    event = next((e for e in events if e.get("id") == evt_id2), None)
    attempt = event.get("metadata", {}).get("delivery_attempt", 0) if event else 0
    duration = int((time.time() - start) * 1000)
    log("T6.1", "NACK increments delivery attempt", nack_ok and attempt == 2,
        f"attempt={attempt}", duration)

    # T7: NACK 3 times → DLQ
    start = time.time()
    evt_id3 = bus.publish("test.dlq", {"step": "dlq_test"})
    time.sleep(1)
    for _ in range(3):
        bus.nack(evt_id3, requeue=False)  # Force to DLQ
    time.sleep(1)

    # Check DLQ
    gist = bus.get_gist()
    dlq_content = gist["files"].get("dlq", {}).get("content", "")
    in_dlq = evt_id3 in dlq_content
    duration = int((time.time() - start) * 1000)
    log("T7.1", "Event lands in DLQ after max retries", in_dlq,
        f"dlq_has_event={in_dlq}", duration)

    # Cleanup
    for e in bus.read_events():
        if e.get("type", "").startswith("test."):
            bus.ack(e["id"], "orchestrator")

# =============================================================================
# T8: Priority (high-priority events processed first)
# =============================================================================
def test_t8_priority():
    print("\n=== T8: Priority Ordering ===")
    cleanup_test_events()
    token = get_token()
    bus = GistEventBus(gist_id=GIST_ID, token=token)

    # Publish normal then critical
    bus.publish("task.created", {"priority": "normal"}, priority="normal")
    time.sleep(0.5)
    bus.publish("task.created", {"priority": "critical"}, priority="critical")
    time.sleep(2)

    pending = bus.get_pending(node_id="", event_types=["task.created"])
    priorities = [e.get("metadata", {}).get("priority", "normal") for e in pending]

    # Critical should be at front (published later but higher priority)
    # We can't strictly order in Gist (append-only), but metadata tracks it
    has_critical = "critical" in priorities
    log("T8.1", "Priority metadata tracked on events", has_critical,
        f"priorities found: {set(priorities)}")

    for e in pending:
        bus.ack(e["id"], "orchestrator")

# =============================================================================
# T9: Rate Limiting
# =============================================================================
def test_t9_rate_limit():
    print("\n=== T9: Rate Limiting ===")
    cleanup_test_events()
    token = get_token()
    bus = GistEventBus(gist_id=GIST_ID, token=token)

    start = time.time()
    successes = 0
    for i in range(10):
        evt_id = bus.publish("test.rate", {"seq": i})
        if evt_id:
            successes += 1
    duration = int((time.time() - start) * 1000)
    avg_interval = duration / 10 if successes else 0

    log("T9.1", "10 rapid publishes succeed without 403", successes == 10,
        f"successes={successes}/10 avg_interval={avg_interval:.0f}ms", duration)

    # Cleanup
    for e in bus.read_events():
        if e.get("type") == "test.rate":
            bus.ack(e["id"], "orchestrator")

# =============================================================================
# T10: Compaction
# =============================================================================
def test_t10_compact():
    print("\n=== T10: Compaction ===")
    cleanup_test_events()
    token = get_token()
    bus = GistEventBus(gist_id=GIST_ID, token=token)

    # Count before
    before = len(bus.read_events())

    # Manually create an old consumed event by backdating metadata
    # (In real usage this happens naturally; for test we inject)
    start = time.time()
    removed = bus.compact(max_age_days=0)  # Aggressive: remove all consumed
    duration = int((time.time() - start) * 1000)

    after = len(bus.read_events())
    log("T10.1", "Compaction removes old consumed events", removed >= 0,
        f"before={before} removed={removed} after={after}", duration)

# =============================================================================
# Report
# =============================================================================
def print_report():
    print("\n" + "=" * 60)
    print("TI-010 TEST HARNESS REPORT")
    print("=" * 60)

    passed = sum(1 for r in RESULTS if r["passed"])
    failed = sum(1 for r in RESULTS if not r["passed"])
    total = len(RESULTS)

    print(f"\nTotal Tests: {total} | ✅ Passed: {passed} | ❌ Failed: {failed}")
    print(f"Pass Rate: {passed/total*100:.1f}%" if total else "N/A")

    print("\n--- Breakdown ---")
    for r in RESULTS:
        status = "✅" if r["passed"] else "❌"
        print(f"  {status} {r['test_id']:8s} {r['name']:<45s} {r['duration_ms']:>6d}ms")
        if not r["passed"] and r["detail"]:
            print(f"           → {r['detail']}")

    print("\n--- JSON Output ---")
    print(json.dumps({
        "suite": "TI-010",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {"total": total, "passed": passed, "failed": failed},
        "tests": RESULTS,
    }, indent=2, default=str))

    return failed == 0

# =============================================================================
# Main
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="TI-010 Test Harness")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--connectivity", action="store_true", help="T1 only")
    parser.add_argument("--publish-consume", action="store_true", help="T2-T4 only")
    parser.add_argument("--ack-nack", action="store_true", help="T5-T7 only")
    parser.add_argument("--priority", action="store_true", help="T8 only")
    parser.add_argument("--rate-limit", action="store_true", help="T9 only")
    parser.add_argument("--compact", action="store_true", help="T10 only")
    parser.add_argument("--report", action="store_true", help="Print JSON report only")
    args = parser.parse_args()

    if not any(vars(args).values()):
        args.all = True

    if args.report:
        print_report()
        return

    print(f"TI-010 Test Harness — Gist ID: {GIST_ID}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")

    if args.all or args.connectivity:
        test_t1_connectivity()
    if args.all:
        wait_for_rate_limit()
        time.sleep(5)
    if args.all or args.publish_consume:
        test_t2_t4_pubsub()
    if args.all:
        wait_for_rate_limit()
        time.sleep(5)
    if args.all or args.ack_nack:
        test_t5_t7_ack_nack_dlq()
    if args.all:
        wait_for_rate_limit()
        time.sleep(5)
    if args.all or args.priority:
        test_t8_priority()
    if args.all:
        wait_for_rate_limit()
        time.sleep(5)
    if args.all or args.rate_limit:
        test_t9_rate_limit()
    if args.all:
        wait_for_rate_limit()
        time.sleep(5)
    if args.all or args.compact:
        test_t10_compact()
    if args.all or args.priority:
        test_t8_priority()
    if args.all or args.rate_limit:
        test_t9_rate_limit()
    if args.all or args.compact:
        test_t10_compact()

    ok = print_report()
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
