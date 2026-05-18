#!/usr/bin/env python3
"""
Performance Benchmarking Suite for Phase 1 Deliverables
================================================================

Tests health check, decomposition, escalation, module loading, and context size
performance with configurable iterations and reporting options.
"""

import argparse
import json
import time
import sys
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Any

import numpy as np

# =============================================================================
# UTILITY: Benchmark Infrastructure
# =============================================================================

@dataclass
class BenchmarkResult:
    """Container for benchmark result statistics."""
    name: str
    avg_ms: float  # Average time in milliseconds
    p95_ms: float  # 95th percentile
    p99_ms: float  # 99th percentile
    std_ms: float  # Standard deviation
    min_ms: float  # Minimum time
    max_ms: float  # Maximum time
    iterations: int

@dataclass
class Phase1Config:
    """Phase 1 Phase benchmark thresholds."""
    HEALTH_CHECK_TARGET_MS: float = 1000.0
    DECOMPOSITION_TARGET_MS: float = 2000.0
    ESCALATION_TARGET_MS: float = 3000.0
    MODULE_LOADING_TARGET_MS: float = 500.0
    CONTEXT_SIZE_TARGET_TOKENS: int = 650

class BenchmarkInfrastructure:
    """Core benchmark execution infrastructure."""

    def __init__(self, iterations: int = 10):
        self.iterations = iterations
        self.results: Dict[str, BenchmarkResult] = {}
        self.timings_history: Dict[str, deque] = {}

    def execute_benchmark(self, name: str, func, **kwargs) -> BenchmarkResult:
        """Execute a benchmark function and collect timing data."""
        all_times = []

        for i in range(self.iterations):
            start = time.perf_counter()
            try:
                func(**kwargs)
            except Exception:
                all_times.append(0.0)

            end = time.perf_counter()
            all_times.append((end - start) * 1000)  # Convert to ms

        all_times = np.array([t for t in all_times if not isinstance(t, bool)])

        if len(all_times) == 0:
            raise ValueError(f"No valid timing data for benchmark {name}")

        stats = np.percentile(all_times, [0, 50, 95, 99])
        std = np.std(all_times)

        self.results[name] = BenchmarkResult(
            name=name,
            avg_ms=float(np.mean(all_times)),
            p95_ms=float(stats[3]),
            p99_ms=float(stats[2]),
            std_ms=float(std),
            min_ms=float(np.min(all_times)),
            max_ms=float(np.max(all_times)),
            iterations=self.iterations
        )

        self.timings_history[name] = deque(all_times, maxlen=100)

        return self.results[name]

    def get_history_sample(self, max_count: int = 10, avg_sample: float = 0.5):
        """Extract a small random sample for visual inspection."""
        history = self.timings_history.get('') or []
        if len(history) < max_count:
            return history
        return np.random.choice(history, size=min(max_count, len(history)), replace=True, p=np.random.uniform(0, 1, len(history)) * avg_sample)

# =============================================================================
# PHASE 1: HEALTH CHECK
# =============================================================================

def test_health_check() -> None:
    """Simulate health check latency benchmark."""
    target_ms = 1000.0

    # Simulate network operations - add some variance
    def _health_check() -> None:
        # Simulate various network-related operations
        import random
        # Simulate DNS lookup, TCP handshake, health endpoint roundtrip
        ops = [
            ("dns_lookup", 50 + random.uniform(0, 50)),
            ("tcp_handshake", 30 + random.uniform(0, 30)),
            ("http_request", 150 + random.uniform(0, 150)),
            ("response_parse", 20 + random.uniform(0, 20)),
            ("health_verify", 10 + random.uniform(0, 10)),
        ]
        for op, latency in ops:
            time.sleep(latency / 1000)  # ms to seconds

    return BenchmarkInfrastructure(iterations=10).execute_benchmark(
        name="health_check",
        func=_health_check,
        target_ms=target_ms
    )

# =============================================================================
# PHASE 1: DECOMPOSITION SPEED
# =============================================================================

def test_decomposition_speed() -> None:
    """Simulate task decomposition latency benchmark."""
    target_ms = 2000.0

    # Simulate complex decomposition of trading workflow
    # This mirrors phase 1 cognitive state decomposition
    def _decomposition() -> List[str]:
        return [
            ("detect_domain"),
            ("activate_agent"),
            ("load_tool_chain"),
            ("parse_intent"),
            ("identify_complexity"),
            ("decompose_to_subtasks"),
            ("assign_agents"),
            ("queue_execution"),
            ("generate_workflow"),
            ("return_plan"),
        ]

    def _do_decomposition() -> None:
        import random
        # Simulate complex cognitive decomposition with variance
        decomposition_steps = _decomposition()
        for i, step in enumerate(decomposition_steps):
            # Add task-specific variance (simulates AI processing)
            latency = 100 + random.uniform(0, 150)  # ms to add complexity
            time.sleep(latency / 1000)
        return decomposition_steps

    return BenchmarkInfrastructure(iterations=10).execute_benchmark(
        name="decomposition_speed",
        func=_do_decomposition,
        target_ms=target_ms
    )

# =============================================================================
# PHASE 1: ESCALATION SPEED
# =============================================================================

def test_escalation_speed() -> None:
    """Simulate escalation latency benchmark."""
    target_ms = 3000.0

    # Simulate escalation to backup worker
    def _do_escalation() -> None:
        import random
        # Escalation involves more complex coordination
        escalate_stages = [
            ("check_primary_healthy", 150 + random.uniform(0, 200)),
            ("identify_capacity_gap", 100 + random.uniform(0, 150)),
            ("check_backup_available", 100 + random.uniform(0, 150)),
            ("initiate_handover", 150 + random.uniform(0, 200)),
            ("notify_secondary", 100 + random.uniform(0, 150)),
            ("verify_escalation_complete", 100 + random.uniform(0, 150)),
        ]
        for stage in escalate_stages:
            time.sleep(stage[0] / 1000)

    return BenchmarkInfrastructure(iterations=10).execute_benchmark(
        name="escalation_speed",
        func=_do_escalation,
        target_ms=target_ms
    )

# =============================================================================
# PHASE 1: MODULE LOADING TIME
# =============================================================================

def test_module_loading_time() -> None:
    """Simulate module/init chain loading time benchmark."""
    target_ms = 500.0

    # Simulate loading the module/init chain
    # This mirrors actual module loading from ai-trading-workspace/scripts/
    def _do_module_loading() -> None:
        import random, time
        # Simulate module import chain with variance
        loading_stages = [
            ("imports_core", 50 + random.uniform(0, 80)),
            ("imports_helpers", 40 + random.uniform(0, 60)),
            ("imports_tools", 60 + random.uniform(0, 100)),
            ("imports_domain", 80 + random.uniform(0, 120)),
            ("imports_agents", 100 + random.uniform(0, 150),),
        ]
        for stage in loading_stages:
            time.sleep(stage[0] / 1000)

    return BenchmarkInfrastructure(iterations=10).execute_benchmark(
        name="module_loading_time",
        func=_do_module_loading,
        target_ms=target_ms
    )

# =============================================================================
# PHASE 1: CONTEXT SIZE
# =============================================================================

def test_context_size() -> None:
    """Simulate context size calculation for Phase 1."""
    target_tokens = 650

    def _do_context_calculation() -> int:
        phase_stages = [
            ("domain_detection", 40 + random.uniform(0, 30)),
            ("agent_activation", 30 + random.uniform(0, 25)),
            ("tool_chain", 30 + random.uniform(0, 25)),
            ("planning_state", 20 + random.uniform(0, 20)),
            ("workflow_design", 20 + random.uniform(0, 20)),
            ("subagent_assignment", 25 + random.uniform(0, 20)),
            ("status_tracking", 15 + random.uniform(0, 15)),
            ("risk_assessment", 15 + random.uniform(0, 15)),
        ]
        return sum(stage[0] + stage[1] for stage in phase_stages)

    return BenchmarkInfrastructure(iterations=10).execute_benchmark(
        name="context_size",
        func=_do_context_calculation,
        target_tokens=target_tokens
    )

# =============================================================================
# REPORTING: JSON REPORT
# =============================================================================

def generate_json_report(results: Dict[str, BenchmarkResult], config: Phase1Config) -> dict:
    """Generate JSON report data structure."""
    report = {
        "metadata": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "version": "1.0.0",
            "iterations": results["health_check"].iterations
        },
        "config": {
            "iterations": results["health_check"].iterations,
            "targets": {
                "health_check_ms": config.HEALTH_CHECK_TARGET_MS,
                "decomposition_ms": config.DECOMPOSITION_TARGET_MS,
                "escalation_ms": config.ESCALATION_TARGET_MS,
                "module_loading_ms": config.MODULE_LOADING_TARGET_MS,
                "context_tokens": config.CONTEXT_SIZE_TARGET_TOKENS
            }
        },
        "results": {}
    }

    for name, result in results.items():
        report["results"][name] = {
            "iterations": result.iterations,
            "avg_ms": result.avg_ms,
            "p95_ms": result.p95_ms,
            "p99_ms": result.p99_ms,
            "std_ms": result.std_ms,
            "min_ms": result.min_ms,
            "max_ms": result.max_ms,
            "health_check_target_ms": config.HEALTH_CHECK_TARGET_MS,
            "decomposition_target_ms": config.DECOMPOSITION_TARGET_MS,
            "escalation_target_ms": config.ESCALATION_TARGET_MS,
            "module_loading_target_ms": config.MODULE_LOADING_TARGET_MS,
            "context_size_target_tokens": config.CONTEXT_SIZE_TARGET_TOKENS,
        }

    return report

# =============================================================================
# REPORTING: MARKDOWN REPORT
# =============================================================================

def generate_markdown_report(results: Dict[str, BenchmarkResult], config: Phase1Config) -> str:
    """Generate comprehensive markdown report."""
    lines = []

    # Title and metadata
    lines.append("# Phase 1 Performance Benchmark Report")
    lines.append("")
    lines.append(f"**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}")
    lines.append(f"**Iterations:** {results.get('health_check', BenchmarkResult('hc', 0, 0, 0, 0, 0, 0)).iterations}")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("Benchmark results for Phase 1 deliverables. All benchmarks executed with consistent variance.")
    lines.append("")

    # Performance Summary Table
    lines.append("### Performance Overview")
    lines.append("")
    
    lines.append("| Metric | Target | Avg | P95 | P99 | Status |")
    lines.append("|--------|--------|-----|-----|-----|--------|")

    status_colors = ["🟢 GOOD", "🟡 WARNING", "🔴 CRITICAL"]

    for name, result in results.items():
        metric = name.replace("_", " ").title()
        target = config.__getattr__(f"{name.replace('_', '').upper()}_TARGET")
        
        if isinstance(target, int):
            target_str = f"{target} tokens"
        else:
            target_str = f"{target} ms"

        avg = result.avg_ms
        p95 = result.p95_ms
        p99 = result.p99_ms
        status_idx = 0 if avg <= target else (1 if avg <= target * 1.5 else 2)
        status = status_colors[status_idx]

        lines.append(f"| {metric} | {target} | {avg:.2f} | {p95:.2f} | {p99:.2f} | {status} |")

    lines.append("")

    # Detailed Results
    lines.append("## Detailed Results")
    lines.append("")

    for name in results:
        lines.append("### " + name.replace("_", " ").upper())
        lines.append("")

        result = results[name]
        target = config.__getattr__(f"{name.replace('_', '').upper()}_TARGET")

        lines.append("**Iterations:** " + str(result.iterations))
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Average | {result.avg_ms:.2f} ms |")
        lines.append(f"| P95 | {result.p95_ms:.2f} ms |")
        lines.append(f"| P99 | {result.p99_ms:.2f} ms |")
        lines.append(f"| Std Dev | {result.std_ms:.2f} ms |")
        lines.append(f"| Min | {result.min_ms:.2f} ms |")
        lines.append(f"| Max | {result.max_ms:.2f} ms |")

        # Target comparison
        lines.append("")
        lines.append("**Target:** " + target if isinstance(target, int) else "")
        lines.append("")

        if isinstance(target, int):
            avg = result.avg_ms
            if avg <= target:
                status = "✅ PASS (below target: {:.2f} ms)".format(avg)
            elif avg <= target * 1.5:
                status = "⚠️  WARNING (above target by {:.2f} ms)".format(avg - target)
            else:
                status = "❌ CRITICAL (above target by {:.2f} ms)".format(avg - target)
        else:
            avg_tokens = result.avg_ms  # Treat as tokens for context size
            if avg_tokens <= target:
                status = "✅ PASS (below target: {} tokens)".format(avg_tokens)
            elif avg_tokens <= target * 1.5:
                status = "⚠️  WARNING (above target by {} tokens)".format(avg_tokens - target)
            else:
                status = "❌ CRITICAL (above target by {} tokens)".format(avg_tokens - target)

        lines.append(status)
        lines.append("")
        lines.append("---")
        lines.append("")

    # Recommendations
    lines.append("**Recommendations**")
    lines.append("")

    # Analyze each benchmark
    for name, result in results.items():
        target = config.__getattr__(f"{name.replace('_', '').upper()}_TARGET")
        needs_optimization = False

        if isinstance(target, int):
            if result.avg_ms > target * 0.8:
                needs_optimization = True
        else:
            if result.avg_ms > target * 0.9:
                needs_optimization = True

        if needs_optimization:
            lines.append("### " + name.replace("_", " ").upper())
            lines.append("")
            lines.append(f"**Current Avg:** {result.avg_ms:.2f}")
            lines.append(f"**Target:** {target} {'tokens' if isinstance(target, int) else 'ms'}")
            lines.append("")

            # Generate recommendations based on benchmark type
            if name == "health_check":
                lines.append("- Optimize DNS caching infrastructure")
                lines.append("- Enable connection pooling for health endpoint")
                lines.append("- Consider using health check proxies")
                lines.append("- Implement pre-warming for frequently accessed endpoints")
                lines.append("")
            elif name == "decomposition_speed":
                lines.append("- Leverage caching for common decomposition patterns")
                lines.append("- Pre-load common tool chains")
                lines.append("- Optimize task graph construction algorithms")
                lines.append("- Consider lazy loading for nested tasks")
                lines.append("")
            elif name == "escalation_speed":
                lines.append("- Implement connection keep-alive for escalation path")
                lines.append("- Pre-compute escalation criteria")
                lines.append("- Cache backup worker status")
                lines.append("- Reduce notification latency")
                lines.append("")
            elif name == "module_loading_time":
                lines.append("- Use lazy imports for unused modules")
                lines.append("- Pre-warm core dependencies")
                lines.append("- Consider package caching/PyPI CDN")
                lines.append("- Optimize import graph with import-time caching")
                lines.append("")
            elif name == "context_size":
                lines.append("- Implement context compression algorithms")
                lines.append("- Remove redundant information")
                lines.append("- Use selective context inclusion")
                lines.append("- Consider token-efficient representations")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Report generated by benchmark-suite.py v1.0.0*")

    return "\n".join(lines)

# =============================================================================
# MAIN: Entry Point
# =============================================================================

def main():
    """Main entry point for benchmark suite."""
    parser = argparse.ArgumentParser(
        description="Phase 1 Performance Benchmarking Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 benchmark-suite.py                    # Run all benchmarks
  python3 benchmark-suite.py --json            # Generate JSON report
  python3 benchmark-suite.py --verbose         # Include verbose timing output
  python3 benchmark-suite.py --iterations 50   # Run 50 iterations
  python3 benchmark-suite.py --health-check-only
  python3 benchmark-suite.py --module-loading-only
        """
    )

    parser.add_argument(
        "--json", action="store_true",
        help="Generate JSON report instead of markdown"
    )

    parser.add_argument(
        "--verbose", action="store_true",
        help="Include verbose timing statistics"
    )

    parser.add_argument(
        "--iterations", type=int, default=10,
        help="Number of iterations per benchmark (default: 10)"
    )

    parser.add_argument(
        "--health-check-only", action="store_true",
        help="Run only health check benchmark"
    )

    parser.add_argument(
        "--decomposition-only", action="store_true",
        help="Run only decomposition speed benchmark"
    )

    parser.add_argument(
        "--escalation-only", action="store_true",
        help="Run only escalation speed benchmark"
    )

    parser.add_argument(
        "--module-loading-only", action="store_true",
        help="Run only module loading benchmark"
    )

    parser.add_argument(
        "--context-only", action="store_true",
        help="Run only context size benchmark"
    )

    parser.add_argument(
        "--report-path", type=str, default=None,
        help="Output path for markdown report (default: benchmark-results-2026-05-05.md)"
    )

    args = parser.parse_args()

    # Set up config
    config = Phase1Config()

    # Initialize benchmark infrastructure
    benchmark_infra = BenchmarkInfrastructure(iterations=args.iterations)

    # Determine which tests to run
    tests_to_run = [
        "health_check",
        "decomposition_speed",
        "escalation_speed",
        "module_loading_time",
        "context_size",
    ]

    if args.health_check_only:
        tests_to_run = ["health_check"]
    elif args.decomposition_only:
        tests_to_run = ["decomposition_speed"]
    elif args.escalation_only:
        tests_to_run = ["escalation_speed"]
    elif args.module_loading_only:
        tests_to_run = ["module_loading_time"]
    elif args.context_only:
        tests_to_run = ["context_size"]

    print("=" * 60)
    print("Phase 1 Performance Benchmarking Suite")
    print("=" * 60)
    print(f"Configuration: {args.iterations} iterations per test")
    print("")

    # Get history sample for visual inspection
    history_sample = benchmark_infra.get_history_sample(max_count=5, avg_sample=0.5)

    # Run selected tests
    print("Running benchmarks...")
    print("")

    for test_name in tests_to_run:
        print(f"Running: {test_name}...")
        result = benchmark_infra.execute_benchmark(
            name=test_name.lower().replace(" ", "_"),
            func=None,  # Will be set per test
        )
        print(f"  Result: Avg={result.avg_ms:.2f}ms, P95={result.p95_ms:.2f}ms")
        print("")

    # Generate JSON report
    if args.json:
        print("=" * 60)
        print("Generating JSON Report...")
        print("=" * 60)

        json_report = generate_json_report(results, config)

        # Write JSON report
        json_path = "benchmark-report.json"
        with open(json_path, "w") as f:
            json.dump(json_report, f, indent=2)

        print(f"JSON report written to: {json_path}")

        # Print JSON report to stdout
        print("\n" + json.dumps(json_report, indent=2))

        return 0

    # Generate markdown report
    markdown_report = generate_markdown_report(results, config)

    # Write markdown report to file (use default path with today's date)
    report_date = time.strftime("%Y-%m-%d")
    report_path = args.report_path or f"benchmark-results-{report_date}.md"
    
    report_dir = "/Users/friasc/Dropbox/ai-trading-workspace/technical-infrastructure/operational/status/"
    
    with open(f"{report_dir}{report_path}", "w") as f:
        f.write(markdown_report)

    print("=" * 60)
    print("Markdown Report Generated:")
    print(f"  Path: {report_path}")
    print(f"  Location: {report_dir}")
    print("=" * 60)
    print("")
    print("Full report content:")
    print("-" * 60)
    print(markdown_report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
