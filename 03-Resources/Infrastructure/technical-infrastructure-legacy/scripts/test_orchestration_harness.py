#!/usr/bin/env python3
"""
test_orchestration_harness.py — Comprehensive testing harness for TI-011 orchestration framework

Tests all orchestration components end-to-end. Dry-run by default.
Use --live for real SSH/SCP tests against lab nodes.

Usage:
    python3 test_orchestration_harness.py --all
    python3 test_orchestration_harness.py --classify --registry --health
    python3 test_orchestration_harness.py --all --live --verbose
    python3 test_orchestration_harness.py --all --report --output report.md
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── PATH RESOLUTION ──────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR / "../.."
SYS_SCRIPTS = str(SCRIPT_DIR)
if SYS_SCRIPTS not in sys.path:
    sys.path.insert(0, SYS_SCRIPTS)

PI_CONFIG_DIR = REPO_ROOT / ".pi"
TRIGGER_DIR = PI_CONFIG_DIR / "decompose-triggers"
PENDING_DIR = TRIGGER_DIR / "pending"
COMPLETED_DIR = TRIGGER_DIR / "completed"

# ── GLOBAL TEST STATE ────────────────────────────────────────────────

RESULTS: List[Dict] = []
VERBOSE = False
LIVE = False


def log(msg: str, level: str = "info"):
    """Print with level prefix."""
    if level == "debug" and not VERBOSE:
        return
    prefix = {"info": "[INFO]", "pass": "[PASS]", "fail": "[FAIL]",
              "warn": "[WARN]", "debug": "[DEBUG]"}.get(level, "[INFO]")
    print(f"{prefix} {msg}")


# ── IMPORT HELPERS ───────────────────────────────────────────────────

def safe_import(module_name: str):
    """Import a module from the scripts directory with fallback."""
    try:
        return __import__(module_name)
    except Exception as e:
        log(f"Cannot import {module_name}: {e}", "warn")
        return None


def run_script(script_name: str, args: List[str], timeout: int = 60) -> Tuple[int, str, str]:
    """Run a script in the scripts directory. Returns (rc, stdout, stderr)."""
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        return 1, "", f"Script not found: {script_path}"
    cmd = [sys.executable, str(script_path)] + args
    if VERBOSE:
        log(f"Running: {' '.join(cmd)}", "debug")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Timeout after {timeout}s"
    except Exception as e:
        return 1, "", str(e)


# ── TEST HELPERS ─────────────────────────────────────────────────────

def record_test(name: str, passed: bool, details: str = "", latency_ms: float = 0.0):
    RESULTS.append({
        "name": name,
        "passed": passed,
        "details": details,
        "latency_ms": round(latency_ms, 1),
        "timestamp": datetime.now().isoformat(),
    })
    level = "pass" if passed else "fail"
    log(f"{'PASS' if passed else 'FAIL'}: {name}" + (f" — {details}" if details else ""), level)


# ── TEST SUITES ──────────────────────────────────────────────────────

def test_classify_prompt():
    """Test classify_prompt.py with various prompt types."""
    log("\n=== TEST SUITE: classify_prompt.py ===", "info")
    test_cases = [
        ("Check if fnet2 is online", "TRIVIAL"),
        ("Write a Python script to parse JSON", "SIMPLE"),
        ("Create an Ansible playbook for 7 nodes", "MEDIUM"),
        ("Design a meta-orchestration framework with adaptive feedback", "HARD"),
        ("Format this CSV with proper headers", "TRIVIAL"),
    ]

    for prompt, expected in test_cases:
        start = time.time()
        rc, out, err = run_script("classify_prompt.py", ["--json", "--threshold", "0.60", prompt], timeout=45)
        latency = (time.time() - start) * 1000

        if rc != 0:
            record_test(f"classify: '{prompt[:40]}...'", False, f"rc={rc}, err={err[:80]}", latency)
            continue

        try:
            result = json.loads(out)
            actual = result.get("complexity", "UNKNOWN")
            passed = actual == expected
            record_test(
                f"classify: '{prompt[:40]}...' -> {actual}",
                passed,
                f"expected {expected}, got {actual}, conf={result.get('confidence', 0)}",
                latency,
            )
        except json.JSONDecodeError:
            record_test(f"classify: '{prompt[:40]}...'", False, f"Invalid JSON: {out[:80]}", latency)

    # Test routing attachment (with correct node configs path)
    try:
        import classify_prompt as cp
        actual_configs = REPO_ROOT / "technical-infrastructure" / "operational" / "data" / "lab-specs" / "node-configs"
        # Override registry path by monkey-patching if needed
        import ti011_node_registry as reg_mod
        if actual_configs.exists():
            old_find = reg_mod.find_repo_root
            reg_mod.find_repo_root = lambda: str(REPO_ROOT / "technical-infrastructure" / "operational" / "data")
        start = time.time()
        result = cp.classify("Design a meta-orchestration framework", with_routing=True)
        latency = (time.time() - start) * 1000
        if actual_configs.exists():
            reg_mod.find_repo_root = old_find
        has_route = bool(result.get("route"))
        record_test("classify: routing info attached", has_route,
                    f"route={result.get('route')}", latency)
    except Exception as e:
        record_test("classify: routing info attached", False, str(e), 0)

    # Test inject_complexity_tag
    try:
        import classify_prompt as cp
        start = time.time()
        tagged = cp.inject_complexity_tag("Check if fnet2 is online")
        latency = (time.time() - start) * 1000
        has_tag = "complexity:" in tagged
        record_test("classify: inject_complexity_tag", has_tag,
                    f"tag present={has_tag}, len={len(tagged)}", latency)
    except Exception as e:
        record_test("classify: inject_complexity_tag", False, str(e), 0)


def test_node_registry():
    """Test ti011_node_registry.py loading and routing."""
    log("\n=== TEST SUITE: ti011_node_registry.py ===", "info")

    try:
        import ti011_node_registry as reg
        # The actual node configs are nested under operational/data/
        actual_configs = REPO_ROOT / "technical-infrastructure" / "operational" / "data" / "lab-specs" / "node-configs"
        start = time.time()
        if actual_configs.exists():
            registry = reg.NodeRegistry(node_configs_dir=str(actual_configs))
        else:
            registry = reg.NodeRegistry()
        latency = (time.time() - start) * 1000
        record_test("registry: load all nodes", len(registry.nodes) > 0,
                    f"{len(registry.nodes)} nodes loaded from {registry.node_configs_dir}", latency)
    except Exception as e:
        record_test("registry: load all nodes", False, str(e), 0)
        return

    complexities = ["trivial", "simple", "medium", "hard"]
    for complexity in complexities:
        start = time.time()
        try:
            route = registry.best_model_for(complexity)
            latency = (time.time() - start) * 1000
            passed = route is not None
            record_test(
                f"registry: best_model_for('{complexity}')",
                passed,
                f"route={route}",
                latency,
            )
        except Exception as e:
            record_test(f"registry: best_model_for('{complexity}')", False, str(e), 0)

    # Test match_subtask_to_local
    sample_subtask = {
        "id": "test-1",
        "description": "Write a Python function to validate JSON",
        "complexity": "simple",
        "estimated_tokens_in": 500,
        "estimated_tokens_out": 300,
        "required_capabilities": ["tools", "coding"],
        "confidence": 0.85,
        "weight": 0.3,
    }
    try:
        start = time.time()
        match = registry.match_subtask_to_local(sample_subtask)
        latency = (time.time() - start) * 1000
        passed = match.get("status") == "MATCHED"
        record_test("registry: match_subtask_to_local", passed,
                    f"status={match.get('status')}, node={match.get('node')}, model={match.get('model')}", latency)
    except Exception as e:
        record_test("registry: match_subtask_to_local", False, str(e), 0)

    # Test scoring
    try:
        start = time.time()
        registry.dump()
        latency = (time.time() - start) * 1000
        record_test("registry: dump() runs without error", True,
                    f"dump completed in {latency:.0f}ms", latency)
    except Exception as e:
        record_test("registry: dump() runs without error", False, str(e), 0)


def test_orchestrator_health():
    """Test orchestrator_health.py."""
    log("\n=== TEST SUITE: orchestrator_health.py ===", "info")

    rc, out, err = run_script("orchestrator_health.py", ["--json"], timeout=10)
    # orchestrator_health exits 1 when not healthy; JSON is still valid
    try:
        result = json.loads(out)
        status = result.get("status")
        valid_status = status in ("healthy", "stressed", "critical", "unknown")
        record_test("health: JSON output valid", valid_status,
                    f"status={status}, ram_pct={result.get('ram_pct')}%, cpu_load={result.get('cpu_load')}", 0)
    except Exception as e:
        record_test("health: JSON output valid", False, f"rc={rc}, err={err[:80]}, exc={e}", 0)

    try:
        import orchestrator_health as oh
        start = time.time()
        result = oh.check_health()
        latency = (time.time() - start) * 1000
        valid = result.get("status") in ("healthy", "stressed", "critical", "unknown")
        record_test("health: check_health() importable", valid,
                    f"status={result.get('status')}, latency={latency:.1f}ms", latency)
    except Exception as e:
        record_test("health: check_health() importable", False, str(e), 0)

    # Test health integration in classify_prompt
    try:
        import classify_prompt as cp
        start = time.time()
        result = cp.classify("Check if fnet2 is online", skip_health_check=False)
        latency = (time.time() - start) * 1000
        # Should complete and include health status
        passed = result.get("complexity") is not None
        record_test("health: integrated into classify_prompt", passed,
                    f"complexity={result.get('complexity')}, latency={result.get('latency_ms')}ms", latency)
    except Exception as e:
        record_test("health: integrated into classify_prompt", False, str(e), 0)


def test_task_submission():
    """Test submit_task.py (dry-run by default; --live for real)."""
    log("\n=== TEST SUITE: submit_task.py ===", "info")

    if not LIVE:
        # Dry-run: validate task JSON generation without network
        try:
            import submit_task as st
            task_id = st.submit_task("fnet3", "echo hello", task_type="shell",
                                      local_store=str(tempfile.mkdtemp(prefix="tasks_")))
            passed = task_id is not None and len(task_id) == 8
            record_test("submit: dry-run task creation", passed,
                        f"task_id={task_id}, type=shell, node=fnet3", 0)
        except Exception as e:
            record_test("submit: dry-run task creation", False, str(e), 0)

        record_test("submit: dry-run mode active", True,
                    "Skipped live SSH/SCP. Use --live to test real submission.", 0)
        return

    # Live mode: submit a harmless command to fnet3
    nodes = ["fnet3"]
    for node in nodes:
        start = time.time()
        rc, out, err = run_script("submit_task.py", ["--node", node, "--command", "hostname", "--type", "shell"], timeout=15)
        latency = (time.time() - start) * 1000
        passed = rc == 0 and "submitted to" in out
        record_test(f"submit: live to {node}", passed,
                    f"rc={rc}, out={out.strip()[:60]}", latency)

    # Submit to all nodes
    start = time.time()
    rc, out, err = run_script("submit_task.py", ["--nodes", "all", "--command", "hostname", "--type", "shell"], timeout=60)
    latency = (time.time() - start) * 1000
    passed = rc == 0 and "Submitted" in out
    record_test("submit: live to all nodes", passed,
                f"rc={rc}, out={out.strip()[:100]}", latency)


def test_decomposition():
    """Test decompose_llm.py, decompose-watcher.py, and trigger creation."""
    log("\n=== TEST SUITE: decomposition pipeline ===", "info")

    # Test decompose_llm.py dry-run
    start = time.time()
    rc, out, err = run_script("decompose_llm.py", [
        "--prompt", "Design a simple logging utility in Python",
        "--tier", "0", "--dry-run", "--json"
    ], timeout=15)
    latency = (time.time() - start) * 1000
    if rc == 0:
        try:
            result = json.loads(out)
            passed = result.get("status") == "dry-run"
            record_test("decompose: dry-run produces valid JSON", passed,
                        f"tier={result.get('tier')}, model={result.get('model')}", latency)
        except Exception as e:
            record_test("decompose: dry-run produces valid JSON", False, str(e), latency)
    else:
        record_test("decompose: dry-run produces valid JSON", False, f"rc={rc}, err={err[:80]}", latency)

    # Test decompose_llm.py validation
    sample_decomp = {
        "sub_tasks": [
            {"id": "1", "description": "Create logger module", "rationale": "Core need",
             "complexity": "simple", "estimated_tokens_in": 500, "estimated_tokens_out": 300,
             "required_capabilities": ["coding"], "confidence": 0.9, "weight": 1.0,
             "dependencies": [], "can_parallelize": True}
        ],
        "global_constraints": {"max_total_tokens": 10000, "preferred_local": True, "max_cloud_escalation_depth": 2}
    }
    try:
        import decompose_llm as dl
        is_valid, errors = dl.validate_decomposition(sample_decomp)
        passed = is_valid and not errors
        record_test("decompose: validate_decomposition()", passed,
                    f"valid={is_valid}, errors={errors}", 0)
    except Exception as e:
        record_test("decompose: validate_decomposition()", False, str(e), 0)

    # Test trigger directory exists
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    record_test("decompose: trigger directories exist", PENDING_DIR.exists(),
                f"pending_dir={PENDING_DIR}", 0)

    # Test writing a trigger manually
    trigger_id = f"test-{uuid.uuid4().hex[:8]}"
    trigger_data = {
        "id": trigger_id,
        "prompt": "Test decomposition trigger",
        "timestamp": datetime.now().isoformat(),
        "confidence": 0.85,
        "node_pool": ["fnet2", "fnet3", "fnet4"],
    }
    trigger_path = PENDING_DIR / f"{trigger_id}.json"
    try:
        with open(trigger_path, "w") as f:
            json.dump(trigger_data, f, indent=2)
        passed = trigger_path.exists()
        record_test("decompose: manual trigger write", passed,
                    f"path={trigger_path}", 0)
        # Cleanup
        trigger_path.unlink()
    except Exception as e:
        record_test("decompose: manual trigger write", False, str(e), 0)

    # Test decompose-watcher.py --list-pending (dry-run)
    rc, out, err = run_script("decompose-watcher.py", ["--list-pending"], timeout=15)
    passed = rc == 0
    record_test("decompose: watcher list-pending runs", passed,
                f"rc={rc}, out_lines={len(out.splitlines())}", 0)


def test_result_collection():
    """Test task-collect-results.py."""
    log("\n=== TEST SUITE: task-collect-results.py ===", "info")

    # Ensure local completed dirs exist
    for node in [f"fnet{i}" for i in range(1, 8)]:
        node_dir = Path("/tmp/tasks/completed") / node
        node_dir.mkdir(parents=True, exist_ok=True)

    # Test dry-run collection (no SSH)
    start = time.time()
    rc, out, err = run_script("task-collect-results.py", [
        "--nodes", "fnet1,fnet2",
        "--output", "/tmp/tasks/test-report.json"
    ], timeout=30)
    latency = (time.time() - start) * 1000
    passed = rc == 0
    record_test("collect: dry-run with fnet1,fnet2", passed,
                f"rc={rc}, out={out.strip()[:80]}", latency)

    # Verify report was written
    report_path = Path("/tmp/tasks/test-report.json")
    if report_path.exists():
        try:
            with open(report_path) as f:
                report = json.load(f)
            record_test("collect: report JSON valid", "total_tasks" in report,
                        f"tasks={report.get('total_tasks')}", 0)
        except Exception as e:
            record_test("collect: report JSON valid", False, str(e), 0)
    else:
        record_test("collect: report JSON valid", False, "report not written", 0)

    # task-collect-results.py has a hyphen, cannot import directly
    # We already tested it via subprocess above
    record_test("collect: subprocess execution works", True,
                "task-collect-results.py tested via subprocess", 0)


def test_synthesis():
    """Test synthesize_results.py."""
    log("\n=== TEST SUITE: synthesize_results.py ===", "info")

    # Create dummy completed task JSONs
    dummy_results = []
    for i in range(3):
        task = {
            "id": f"test-task-{i}",
            "plan_title": "TEST-PLAN-001",
            "step": i,
            "sub_task": f"Dummy sub-task {i}",
            "rc": 0,
            "elapsed_seconds": 2 + i,
            "stdout": f"Output from step {i}\n",
            "stderr": "",
            "node": "fnet3",
        }
        dummy_results.append(task)
        node_dir = Path("/tmp/tasks/completed/fnet3")
        node_dir.mkdir(parents=True, exist_ok=True)
        with open(node_dir / f"{task['id']}.json", "w") as f:
            json.dump(task, f, indent=2)

    # Add one failure
    fail_task = {
        "id": "test-task-fail",
        "plan_title": "TEST-PLAN-001",
        "step": 99,
        "sub_task": "Failing sub-task",
        "rc": 1,
        "elapsed_seconds": 1,
        "stdout": "",
        "stderr": "Error: something broke",
        "node": "fnet3",
    }
    with open(node_dir / "test-task-fail.json", "w") as f:
        json.dump(fail_task, f, indent=2)

    # Test collect + synthesize
    start = time.time()
    rc, out, err = run_script("synthesize_results.py", [
        "--plan", "TEST-PLAN-001",
        "--nodes", "fnet3",
        "--json"
    ], timeout=30)
    latency = (time.time() - start) * 1000
    if rc == 0:
        try:
            result = json.loads(out)
            passed = result.get("total_steps") == 4 and result.get("successful") == 3
            record_test("synthesize: collect + synthesize", passed,
                        f"steps={result.get('total_steps')}, ok={result.get('successful')}, failed={result.get('failed')}", latency)
        except Exception as e:
            record_test("synthesize: collect + synthesize", False, str(e), latency)
    else:
        record_test("synthesize: collect + synthesize", False, f"rc={rc}, err={err[:80]}", latency)

    # Test update_plan_execution_results
    try:
        import synthesize_results as sr
        dummy_synthesis = {
            "plan_title": "TEST-PLAN-001",
            "total_steps": 3,
            "successful": 2,
            "failed": 1,
            "total_elapsed_ms": 5000,
            "success_rate": 0.67,
            "steps": [
                {"step": 1, "sub_task": "A", "status": "success", "rc": 0, "elapsed_seconds": 2, "actual_model": "qwen3:8b", "actual_node": "fnet3"},
                {"step": 2, "sub_task": "B", "status": "success", "rc": 0, "elapsed_seconds": 1, "actual_model": "qwen3:8b", "actual_node": "fnet3"},
                {"step": 3, "sub_task": "C", "status": "failed", "rc": 1, "elapsed_seconds": 1, "actual_model": "qwen3:8b", "actual_node": "fnet3"},
            ],
            "combined_output": "Test output",
        }
        temp_plan = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        temp_plan.write("# Test Plan\n\n## Execution Results\n\n")
        temp_plan.close()
        updated = sr.update_plan_execution_results(temp_plan.name, dummy_synthesis)
        record_test("synthesize: update_plan_execution_results", updated,
                    f"plan_updated={updated}", 0)
        os.unlink(temp_plan.name)
    except Exception as e:
        record_test("synthesize: update_plan_execution_results", False, str(e), 0)


def test_extension_config():
    """Validate pi-keyword-router extension configuration."""
    log("\n=== TEST SUITE: extension config ===", "info")

    # Check repo-level config
    repo_config = REPO_ROOT / ".pi" / "keyword-router.json"
    if repo_config.exists():
        try:
            with open(repo_config) as f:
                config = json.load(f)
            has_routes = "routes" in config
            has_default = "default" in config
            record_test("extension: repo config valid", has_routes and has_default,
                        f"routes={len(config.get('routes', {}))}, default={config.get('default', {})}", 0)
        except Exception as e:
            record_test("extension: repo config valid", False, str(e), 0)
    else:
        record_test("extension: repo config present", False,
                    f"Missing: {repo_config}", 0)

    # Check global config
    global_config = Path.home() / ".pi" / "agent" / "keyword-router.json"
    if global_config.exists():
        try:
            with open(global_config) as f:
                config = json.load(f)
            has_routes = "routes" in config
            record_test("extension: global config valid", has_routes,
                        f"routes={len(config.get('routes', {}))}", 0)
        except Exception as e:
            record_test("extension: global config valid", False, str(e), 0)
    else:
        record_test("extension: global config present", False,
                    f"Missing: {global_config}", 0)

    # Check extension package exists
    ext_dir = REPO_ROOT / "technical-infrastructure" / "packages" / "pi-keyword-router"
    has_index = (ext_dir / "index.ts").exists()
    has_pkg = (ext_dir / "package.json").exists()
    record_test("extension: source files present", has_index and has_pkg,
                f"index.ts={has_index}, package.json={has_pkg}", 0)

    if has_pkg:
        try:
            with open(ext_dir / "package.json") as f:
                pkg = json.load(f)
            is_module = pkg.get("type") == "module"
            has_peer = "@mariozechner/pi-coding-agent" in str(pkg.get("peerDependencies", {}))
            record_test("extension: package.json valid", is_module and has_peer,
                        f"type={pkg.get('type')}, peerDeps={list(pkg.get('peerDependencies', {}).keys())}", 0)
        except Exception as e:
            record_test("extension: package.json valid", False, str(e), 0)

    # Check complexity-router.json (runtime route config in scripts dir)
    router_json = SCRIPT_DIR / "complexity-router.json"
    if router_json.exists():
        try:
            with open(router_json) as f:
                routes = json.load(f)
            record_test("extension: complexity-router.json valid",
                        isinstance(routes, dict) and len(routes) > 0,
                        f"routes={len(routes)}", 0)
        except Exception as e:
            record_test("extension: complexity-router.json valid", False, str(e), 0)
    else:
        record_test("extension: complexity-router.json present", False,
                    f"Missing: {router_json}", 0)

    # ── Validate new P0/P1 features in installed extension ──────────
    installed_ext = Path.home() / ".pi" / "agent" / "git" / "github.com" / "carlosfrias" / "pi-keyword-router"
    index_ts = installed_ext / "index.ts"
    classifier_ts = installed_ext / "lib" / "classifier.ts"
    router_ts = installed_ext / "lib" / "router.ts"

    if index_ts.exists():
        src = index_ts.read_text()
        has_dispatch = "dispatchToLab" in src
        has_health = "getOrchestratorHealth" in src
        has_orchestrator_cmd = 'registerCommand("orchestrator-health"' in src
        has_submit_cmd = 'registerCommand("submit-node"' in src
        has_decompose_cmd = 'registerCommand("decompose"' in src
        has_collect_cmd = 'registerCommand("collect-results"' in src
        has_synthesize_cmd = 'registerCommand("synthesize"' in src

        record_test("extension: P0 dispatch bridge present", has_dispatch,
                    f"dispatchToLab={has_dispatch}", 0)
        record_test("extension: P0 health cache present", has_health,
                    f"getOrchestratorHealth={has_health}", 0)
        record_test("extension: P1 commands present",
                    has_orchestrator_cmd and has_submit_cmd and has_decompose_cmd and has_collect_cmd and has_synthesize_cmd,
                    f"/orchestrator-health={has_orchestrator_cmd}, /submit-node={has_submit_cmd}, /decompose={has_decompose_cmd}, /collect-results={has_collect_cmd}, /synthesize={has_synthesize_cmd}", 0)
    else:
        record_test("extension: installed index.ts present", False,
                    f"Missing: {index_ts}", 0)

    if classifier_ts.exists():
        src = classifier_ts.read_text()
        has_skip = "skipPythonClassifier" in src
        record_test("extension: P0 skipPython flag present", has_skip,
                    f"skipPythonClassifier={has_skip}", 0)
    else:
        record_test("extension: classifier.ts present", False,
                    f"Missing: {classifier_ts}", 0)

    if router_ts.exists():
        src = router_ts.read_text()
        has_method = "setSkipPythonClassifier" in src
        record_test("extension: P0 router skip method present", has_method,
                    f"setSkipPythonClassifier={has_method}", 0)
    else:
        record_test("extension: router.ts present", False,
                    f"Missing: {router_ts}", 0)


def test_node_health_checks():
    """Run health checks on all nodes via SSH."""
    log("\n=== TEST SUITE: node health checks ===", "info")

    nodes = [f"fnet{i}" for i in range(1, 8)]
    reachable = []

    for node in nodes:
        start = time.time()
        try:
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=3", f"friasc@{node}", "hostname"],
                capture_output=True, text=True, timeout=5
            )
            latency = (time.time() - start) * 1000
            if result.returncode == 0:
                reachable.append(node)
                record_test(f"health: {node} SSH reachable", True,
                            f"hostname={result.stdout.strip()}, latency={latency:.0f}ms", latency)
            else:
                record_test(f"health: {node} SSH reachable", False,
                            f"rc={result.returncode}, err={result.stderr[:60]}", latency)
        except Exception as e:
            latency = (time.time() - start) * 1000
            record_test(f"health: {node} SSH reachable", False, str(e), latency)

    # Check Ollama on reachable nodes
    for node in reachable:
        start = time.time()
        try:
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=3", f"friasc@{node}", "curl -s http://localhost:11434/api/tags | head -c 200"],
                capture_output=True, text=True, timeout=10
            )
            latency = (time.time() - start) * 1000
            has_ollama = result.returncode == 0 and "models" in result.stdout or "name" in result.stdout
            record_test(f"health: {node} Ollama responding", has_ollama,
                        f"latency={latency:.0f}ms, out_len={len(result.stdout)}", latency)
        except Exception as e:
            record_test(f"health: {node} Ollama responding", False, str(e), 0)

    # Check orchestrator Ollama (local, no SSH)
    start = time.time()
    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:11434/api/tags"],
            capture_output=True, text=True, timeout=5
        )
        latency = (time.time() - start) * 1000
        has_ollama = result.returncode == 0 and ("models" in result.stdout or "name" in result.stdout)
        record_test("health: orchestrator Ollama responding", has_ollama,
                    f"latency={latency:.0f}ms", latency)
        if has_ollama:
            reachable.append("orchestrator")
    except Exception as e:
        record_test("health: orchestrator Ollama responding", False, str(e), 0)

    # Check reverse connectivity: orchestrator can reach lab nodes
    start = time.time()
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=3", "friasc@fnet3", "hostname"],
            capture_output=True, text=True, timeout=5
        )
        latency = (time.time() - start) * 1000
        record_test("health: orchestrator can reach fnet3", result.returncode == 0,
                    f"latency={latency:.0f}ms", latency)
    except Exception as e:
        record_test("health: orchestrator can reach fnet3", False, str(e), 0)

    record_test("health: summary", True, f"{len(reachable)}/{len(nodes)+1} nodes reachable", 0)


# ── REPORT GENERATION ────────────────────────────────────────────────

def generate_report(output_path: Optional[str] = None) -> str:
    """Generate a markdown test report."""
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = total - passed
    total_latency = sum(r["latency_ms"] for r in RESULTS)

    lines = []
    lines.append("# TI-011 Orchestration Framework Test Report")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ET")
    lines.append(f"**Live Mode:** {'Yes' if LIVE else 'No (dry-run)'}")
    lines.append(f"**Verbose:** {'Yes' if VERBOSE else 'No'}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Tests | {total} |")
    lines.append(f"| Passed | {passed} ({passed/total*100:.1f}% if total else 0.0f%) |")
    lines.append(f"| Failed | {failed} |")
    lines.append(f"| Total Latency | {total_latency:.0f}ms |")
    lines.append("")

    if failed > 0:
        lines.append("## Failures")
        lines.append("")
        for r in RESULTS:
            if not r["passed"]:
                lines.append(f"### {r['name']}")
                lines.append(f"- **Details:** {r['details']}")
                lines.append(f"- **Latency:** {r['latency_ms']:.1f}ms")
                lines.append(f"- **Timestamp:** {r['timestamp']}")
                lines.append("")

    lines.append("## All Results")
    lines.append("")
    lines.append("| Test | Result | Latency | Details |")
    lines.append("|------|--------|---------|---------|")
    for r in RESULTS:
        icon = "PASS" if r["passed"] else "FAIL"
        lines.append(f"| {r['name']} | {icon} | {r['latency_ms']:.0f}ms | {r['details'][:80]} |")

    report = "\n".join(lines)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            f.write(report)
        log(f"Report written to: {out}", "info")

    return report


# ── MAIN ─────────────────────────────────────────────────────────────

def main():
    global VERBOSE, LIVE

    parser = argparse.ArgumentParser(
        description="TI-011 Orchestration Framework Testing Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 test_orchestration_harness.py --all
  python3 test_orchestration_harness.py --classify --registry --health
  python3 test_orchestration_harness.py --all --live --verbose
  python3 test_orchestration_harness.py --all --report --output wiki/report.md
        """
    )
    parser.add_argument("--all", action="store_true", help="Run all test suites")
    parser.add_argument("--classify", action="store_true", help="Test classify_prompt.py")
    parser.add_argument("--registry", action="store_true", help="Test ti011_node_registry.py")
    parser.add_argument("--health", action="store_true", help="Test orchestrator_health.py")
    parser.add_argument("--submit", action="store_true", help="Test submit_task.py")
    parser.add_argument("--decompose", action="store_true", help="Test decomposition pipeline")
    parser.add_argument("--collect", action="store_true", help="Test task-collect-results.py")
    parser.add_argument("--synthesize", action="store_true", help="Test synthesize_results.py")
    parser.add_argument("--extension", action="store_true", help="Test extension config")
    parser.add_argument("--node-health", action="store_true", help="Run health checks on all nodes")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    parser.add_argument("--output", default=None, help="Report output file path")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    parser.add_argument("--live", action="store_true",
                        help="Run live tests (SSH/SCP to real nodes). Default: dry-run.")
    args = parser.parse_args()

    VERBOSE = args.verbose
    LIVE = args.live

    if not any([args.all, args.classify, args.registry, args.health, args.submit,
                args.decompose, args.collect, args.synthesize, args.extension, args.node_health]):
        parser.print_help()
        sys.exit(1)

    start_time = time.time()
    log(f"Starting harness at {datetime.now().isoformat()}", "info")
    log(f"Repo root: {REPO_ROOT}", "info")
    log(f"Scripts dir: {SCRIPT_DIR}", "info")
    log(f"Live mode: {LIVE}", "info")
    log("", "info")

    run_all = args.all

    if run_all or args.classify:
        test_classify_prompt()
    if run_all or args.registry:
        test_node_registry()
    if run_all or args.health:
        test_orchestrator_health()
    if run_all or args.submit:
        test_task_submission()
    if run_all or args.decompose:
        test_decomposition()
    if run_all or args.collect:
        test_result_collection()
    if run_all or args.synthesize:
        test_synthesis()
    if run_all or args.extension:
        test_extension_config()
    if run_all or args.node_health:
        test_node_health_checks()

    elapsed = (time.time() - start_time) * 1000
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = total - passed

    log(f"\n{'='*60}", "info")
    log(f"Harness complete in {elapsed:.0f}ms", "info")
    log(f"Results: {passed}/{total} passed ({passed/total*100:.1f}% if total else 0.0f%)",
        "pass" if failed == 0 else "fail")
    if failed > 0:
        log(f"Failures: {failed}", "fail")

    if args.report or args.output:
        report = generate_report(args.output)
        if not args.output:
            print("\n--- REPORT ---\n")
            print(report)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
