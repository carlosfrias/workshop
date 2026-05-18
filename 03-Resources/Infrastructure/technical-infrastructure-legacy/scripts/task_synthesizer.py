#!/usr/bin/env python3
"""
task_synthesizer.py — Result Synthesis Engine (P1.2)

Combines results from binary-decomposed sub-tasks into a unified response.
Handles partial failures, generates synthesis metrics, and logs results.

Usage:
    # Synthesize results from sub-tasks
    python3 task_synthesizer.py --results result1.json result2.json

    # Test mode
    python3 task_synthesizer.py --test

    # With output file
    python3 task_synthesizer.py --results *.json --output synthesis.json

Output: Unified synthesis result with metrics
"""
import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_result_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load a single result JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        print(f"Warning: Could not load {filepath}: {e}", file=sys.stderr)
        return None


def load_results_from_directory(dir_path: str, pattern: str = "*.json") -> List[Dict[str, Any]]:
    """Load all result JSON files from a directory."""
    results = []
    dir_path = Path(dir_path)
    
    if not dir_path.exists():
        return results
    
    for filepath in dir_path.glob(pattern):
        result = load_result_file(str(filepath))
        if result:
            results.append(result)
    
    return results


def validate_sub_task(result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a sub-task result and extract key metadata."""
    validation = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check required fields
    required_fields = ["id", "status"]
    for field in required_fields:
        if field not in result:
            validation["valid"] = False
            validation["errors"].append(f"Missing required field: {field}")
    
    # Check for execution metadata
    if "stdout" not in result and "output" not in result and "result" not in result:
        validation["warnings"].append("No output data found")
    
    # Check for errors
    if result.get("rc", 0) != 0:
        validation["warnings"].append(f"Non-zero return code: {result.get('rc')}")
    
    if result.get("stderr"):
        validation["warnings"].append("Stderr output present")
    
    # Check timing
    if "elapsed_seconds" not in result and "duration" not in result:
        validation["warnings"].append("No timing information")
    
    return validation


def combine_outputs(results: List[Dict[str, Any]], strategy: str = "sequential") -> str:
    """
    Combine outputs from multiple sub-tasks.
    
    Args:
        results: List of sub-task results
        strategy: Combination strategy (sequential, merge, aggregate)
    
    Returns:
        Combined output string
    """
    if not results:
        return ""
    
    if strategy == "sequential":
        # Order by part/depth and concatenate
        sorted_results = sorted(
            results,
            key=lambda r: (r.get("depth", 0), r.get("part", "A"))
        )
        
        outputs = []
        for r in sorted_results:
            output = r.get("stdout") or r.get("output") or r.get("result") or ""
            if output:
                outputs.append(f"--- {r.get('id', 'Unknown')} ---\n{output}")
        
        return "\n\n".join(outputs)
    
    elif strategy == "merge":
        # Merge JSON outputs if possible
        merged = {}
        for r in results:
            output = r.get("stdout") or r.get("output") or r.get("result") or ""
            try:
                data = json.loads(output)
                merged.update(data)
            except (json.JSONDecodeError, TypeError):
                # Non-JSON output, just concatenate
                pass
        
        if merged:
            return json.dumps(merged, indent=2)
        else:
            # Fallback to sequential
            return combine_outputs(results, strategy="sequential")
    
    elif strategy == "aggregate":
        # Aggregate numeric results
        numeric_values = []
        text_outputs = []
        
        for r in results:
            output = r.get("stdout") or r.get("output") or r.get("result") or ""
            try:
                data = json.loads(output)
                if isinstance(data, (int, float)):
                    numeric_values.append(data)
                elif isinstance(data, dict) and "value" in data:
                    numeric_values.append(data["value"])
            except (json.JSONDecodeError, TypeError):
                text_outputs.append(output)
        
        if numeric_values:
            return json.dumps({
                "count": len(numeric_values),
                "sum": sum(numeric_values),
                "average": sum(numeric_values) / len(numeric_values),
                "min": min(numeric_values),
                "max": max(numeric_values)
            }, indent=2)
        else:
            return "\n\n".join(text_outputs)
    
    else:
        return combine_outputs(results, strategy="sequential")


def handle_partial_failures(
    results: List[Dict[str, Any]],
    synthesis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle partial failures in sub-task results.
    
    Args:
        results: List of sub-task results
        synthesis: Current synthesis dict
    
    Returns:
        Updated synthesis with failure handling
    """
    successful = [r for r in results if r.get("rc", 0) == 0 and r.get("status") == "success"]
    failed = [r for r in results if r.get("rc", 0) != 0 or r.get("status") != "success"]
    
    synthesis["partial_failure"] = len(failed) > 0 and len(successful) > 0
    synthesis["complete_failure"] = len(failed) == len(results)
    synthesis["failure_details"] = {
        "successful_count": len(successful),
        "failed_count": len(failed),
        "failed_task_ids": [r.get("id") for r in failed],
        "success_rate": len(successful) / len(results) if results else 0
    }
    
    if synthesis["complete_failure"]:
        synthesis["synthesis_status"] = "failed"
        synthesis["recommendation"] = "All sub-tasks failed. Consider re-decomposition or manual intervention."
    elif synthesis["partial_failure"]:
        synthesis["synthesis_status"] = "partial"
        synthesis["recommendation"] = "Some sub-tasks succeeded. Review failed tasks and consider re-execution."
        
        # Try to salvage partial results
        if successful:
            synthesis["partial_output"] = combine_outputs(successful)
            synthesis["recommendation"] += " Partial results available from successful tasks."
    else:
        synthesis["synthesis_status"] = "success"
        synthesis["recommendation"] = "All sub-tasks completed successfully."
    
    return synthesis


def calculate_synthesis_metrics(
    results: List[Dict[str, Any]],
    synthesis: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate synthesis performance metrics."""
    metrics = {
        "total_sub_tasks": len(results),
        "successful_tasks": sum(1 for r in results if r.get("rc", 0) == 0),
        "failed_tasks": sum(1 for r in results if r.get("rc", 0) != 0),
        "total_elapsed_seconds": 0,
        "average_elapsed_seconds": 0,
        "max_elapsed_seconds": 0,
        "min_elapsed_seconds": float('inf'),
        "output_size_bytes": 0,
        "synthesis_timestamp": datetime.now().isoformat()
    }
    
    elapsed_times = []
    output_sizes = []
    
    for r in results:
        # Elapsed time
        elapsed = r.get("elapsed_seconds") or r.get("duration") or 0
        if elapsed:
            elapsed_times.append(elapsed)
        
        # Output size
        output = r.get("stdout") or r.get("output") or r.get("result") or ""
        output_sizes.append(len(output.encode('utf-8')))
    
    if elapsed_times:
        metrics["total_elapsed_seconds"] = sum(elapsed_times)
        metrics["average_elapsed_seconds"] = sum(elapsed_times) / len(elapsed_times)
        metrics["max_elapsed_seconds"] = max(elapsed_times)
        metrics["min_elapsed_seconds"] = min(elapsed_times)
    else:
        metrics["min_elapsed_seconds"] = 0
    
    metrics["output_size_bytes"] = sum(output_sizes)
    
    # Calculate efficiency score (0-100)
    if results:
        success_rate = metrics["successful_tasks"] / len(results)
        # Penalize for failures and long execution
        efficiency = success_rate * 100
        if metrics["total_elapsed_seconds"] > 60:
            efficiency *= 0.9  # 10% penalty for > 1 minute
        if metrics["total_elapsed_seconds"] > 300:
            efficiency *= 0.8  # Additional penalty for > 5 minutes
        
        metrics["efficiency_score"] = round(efficiency, 2)
    else:
        metrics["efficiency_score"] = 0
    
    return metrics


def synthesize_results(
    results: List[Dict[str, Any]],
    original_task: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main synthesis function - combine sub-task results into unified response.
    
    Args:
        results: List of sub-task results
        original_task: Original task before decomposition (optional)
    
    Returns:
        Unified synthesis result
    """
    if not results:
        return {
            "synthesis_status": "failed",
            "error": "No results to synthesize",
            "timestamp": datetime.now().isoformat()
        }
    
    # Validate all results
    validations = [validate_sub_task(r) for r in results]
    invalid_results = [i for i, v in enumerate(validations) if not v["valid"]]
    
    if invalid_results:
        # Filter out invalid results
        print(f"Warning: {len(invalid_results)} invalid results filtered out", file=sys.stderr)
        results = [r for i, r in enumerate(results) if i not in invalid_results]
    
    # Initialize synthesis
    synthesis = {
        "synthesis_id": f"synth-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "original_task_id": original_task.get("id") if original_task else None,
        "synthesis_status": "pending",
        "timestamp": datetime.now().isoformat(),
        "sub_task_results": results,
        "combined_output": "",
        "metrics": {},
        "failure_details": {},
        "recommendation": ""
    }
    
    # Combine outputs
    synthesis["combined_output"] = combine_outputs(results, strategy="sequential")
    
    # Handle partial failures
    synthesis = handle_partial_failures(results, synthesis)
    
    # Calculate metrics
    synthesis["metrics"] = calculate_synthesis_metrics(results, synthesis)
    
    # Add validation summary
    synthesis["validation_summary"] = {
        "total_validated": len(validations),
        "valid_count": sum(1 for v in validations if v["valid"]),
        "warnings": sum(len(v["warnings"]) for v in validations),
        "errors": sum(len(v["errors"]) for v in validations)
    }
    
    # Log synthesis
    log_synthesis(synthesis)
    
    return synthesis


def log_synthesis(synthesis: Dict[str, Any]):
    """Log synthesis event to JSONL file."""
    script_dir = Path(__file__).parent.absolute()
    log_dir = script_dir.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "task_synthesis.jsonl"
    
    # Create compact log entry (don't log full output)
    log_entry = {
        "timestamp": synthesis["timestamp"],
        "synthesis_id": synthesis["synthesis_id"],
        "original_task_id": synthesis.get("original_task_id"),
        "synthesis_status": synthesis["synthesis_status"],
        "total_sub_tasks": synthesis["metrics"].get("total_sub_tasks", 0),
        "successful_tasks": synthesis["metrics"].get("successful_tasks", 0),
        "efficiency_score": synthesis["metrics"].get("efficiency_score", 0),
        "total_elapsed_seconds": synthesis["metrics"].get("total_elapsed_seconds", 0),
        "output_size_bytes": synthesis["metrics"].get("output_size_bytes", 0),
        "partial_failure": synthesis.get("partial_failure", False),
        "recommendation": synthesis.get("recommendation", "")[:200]
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def print_synthesis_result(synthesis: Dict[str, Any], verbose: bool = False):
    """Print synthesis result in human-readable format."""
    print("=" * 70)
    print("TASK SYNTHESIS RESULT")
    print("=" * 70)
    print(f"Synthesis ID: {synthesis['synthesis_id']}")
    print(f"Status: {synthesis['synthesis_status'].upper()}")
    print(f"Timestamp: {synthesis['timestamp']}")
    print()
    
    if synthesis.get("error"):
        print(f"ERROR: {synthesis['error']}")
        print()
    
    # Metrics
    metrics = synthesis.get("metrics", {})
    if metrics:
        print("METRICS")
        print("-" * 70)
        print(f"  Total Sub-tasks: {metrics.get('total_sub_tasks', 0)}")
        print(f"  Successful: {metrics.get('successful_tasks', 0)}")
        print(f"  Failed: {metrics.get('failed_tasks', 0)}")
        print(f"  Success Rate: {metrics.get('successful_tasks', 0) / max(1, metrics.get('total_sub_tasks', 1)) * 100:.1f}%")
        print(f"  Total Elapsed: {metrics.get('total_elapsed_seconds', 0):.2f}s")
        print(f"  Average Elapsed: {metrics.get('average_elapsed_seconds', 0):.2f}s")
        print(f"  Output Size: {metrics.get('output_size_bytes', 0):,} bytes")
        print(f"  Efficiency Score: {metrics.get('efficiency_score', 0)}/100")
        print()
    
    # Failure details
    if synthesis.get("partial_failure") or synthesis.get("complete_failure"):
        print("FAILURE DETAILS")
        print("-" * 70)
        failure_details = synthesis.get("failure_details", {})
        print(f"  Failed Task IDs: {failure_details.get('failed_task_ids', [])}")
        print(f"  Success Rate: {failure_details.get('success_rate', 0) * 100:.1f}%")
        print()
    
    # Recommendation
    if synthesis.get("recommendation"):
        print("RECOMMENDATION")
        print("-" * 70)
        print(f"  {synthesis['recommendation']}")
        print()
    
    # Combined output (truncated)
    if synthesis.get("combined_output"):
        print("COMBINED OUTPUT (first 500 chars)")
        print("-" * 70)
        output = synthesis["combined_output"]
        if len(output) > 500:
            print(output[:500] + "...")
            print(f"\n[Output truncated - {len(output)} total chars]")
        else:
            print(output)
        print()
    
    # Validation summary
    validation = synthesis.get("validation_summary", {})
    if validation:
        print("VALIDATION")
        print("-" * 70)
        print(f"  Validated: {validation.get('total_validated', 0)}")
        print(f"  Valid: {validation.get('valid_count', 0)}")
        print(f"  Warnings: {validation.get('warnings', 0)}")
        print(f"  Errors: {validation.get('errors', 0)}")
        print()
    
    print("=" * 70)


def run_tests():
    """Run test suite for task synthesizer."""
    print("Running Task Synthesizer Tests")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Synthesize successful results
    print("\n[Test 1] Synthesize successful results")
    mock_results = [
        {
            "id": "task-1-a",
            "status": "success",
            "rc": 0,
            "stdout": "Result from part A",
            "elapsed_seconds": 2.5,
            "part": "A",
            "depth": 1
        },
        {
            "id": "task-1-b",
            "status": "success",
            "rc": 0,
            "stdout": "Result from part B",
            "elapsed_seconds": 3.0,
            "part": "B",
            "depth": 1
        }
    ]
    
    synthesis = synthesize_results(mock_results)
    
    if (synthesis["synthesis_status"] == "success" and
        synthesis["metrics"]["successful_tasks"] == 2 and
        "Result from part A" in synthesis["combined_output"]):
        print("  ✅ PASS: Successfully synthesized results")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Synthesis failed")
        tests_failed += 1
    
    # Test 2: Handle partial failures
    print("\n[Test 2] Handle partial failures")
    mock_results = [
        {
            "id": "task-2-a",
            "status": "success",
            "rc": 0,
            "stdout": "Success result",
            "elapsed_seconds": 1.0
        },
        {
            "id": "task-2-b",
            "status": "failed",
            "rc": 1,
            "stderr": "Error occurred",
            "elapsed_seconds": 0.5
        }
    ]
    
    synthesis = synthesize_results(mock_results)
    
    if (synthesis.get("partial_failure") and
        synthesis["synthesis_status"] == "partial" and
        synthesis["metrics"]["successful_tasks"] == 1):
        print("  ✅ PASS: Partial failure handled correctly")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Partial failure not handled")
        tests_failed += 1
    
    # Test 3: Handle complete failure
    print("\n[Test 3] Handle complete failure")
    mock_results = [
        {
            "id": "task-3-a",
            "status": "failed",
            "rc": 1,
            "stderr": "Error A"
        },
        {
            "id": "task-3-b",
            "status": "failed",
            "rc": 2,
            "stderr": "Error B"
        }
    ]
    
    synthesis = synthesize_results(mock_results)
    
    if (synthesis.get("complete_failure") and
        synthesis["synthesis_status"] == "failed"):
        print("  ✅ PASS: Complete failure handled correctly")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Complete failure not handled")
        tests_failed += 1
    
    # Test 4: Metrics calculation
    print("\n[Test 4] Metrics calculation accuracy")
    mock_results = [
        {"id": "t1", "status": "success", "rc": 0, "elapsed_seconds": 10, "stdout": "a" * 100},
        {"id": "t2", "status": "success", "rc": 0, "elapsed_seconds": 20, "stdout": "b" * 200},
        {"id": "t3", "status": "failed", "rc": 1, "elapsed_seconds": 5, "stdout": "c" * 50}
    ]
    
    synthesis = synthesize_results(mock_results)
    metrics = synthesis["metrics"]
    
    if (metrics["total_sub_tasks"] == 3 and
        metrics["successful_tasks"] == 2 and
        metrics["total_elapsed_seconds"] == 35 and
        abs(metrics["average_elapsed_seconds"] - 11.67) < 0.1):
        print("  ✅ PASS: Metrics calculated correctly")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Metrics incorrect")
        tests_failed += 1
    
    # Test 5: Empty results handling
    print("\n[Test 5] Empty results handling")
    synthesis = synthesize_results([])
    
    if synthesis["synthesis_status"] == "failed" and "error" in synthesis:
        print("  ✅ PASS: Empty results handled correctly")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Empty results not handled")
        tests_failed += 1
    
    # Test 6: Output combination strategies
    print("\n[Test 6] Output combination (sequential strategy)")
    mock_results = [
        {"id": "t1", "part": "A", "stdout": "Part A output"},
        {"id": "t2", "part": "B", "stdout": "Part B output"}
    ]
    
    combined = combine_outputs(mock_results, strategy="sequential")
    
    if "Part A output" in combined and "Part B output" in combined:
        print("  ✅ PASS: Outputs combined correctly")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Output combination failed")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"TESTS PASSED: {tests_passed}/{tests_passed + tests_failed}")
    print("=" * 70)
    
    return tests_failed == 0


def main():
    parser = argparse.ArgumentParser(
        description="Task Result Synthesizer - Combine sub-task results"
    )
    parser.add_argument(
        "--results",
        nargs="+",
        help="Result JSON files to synthesize"
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Directory containing result JSON files"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="Glob pattern for result files (default: *.json)"
    )
    parser.add_argument(
        "--original-task",
        type=str,
        help="Original task JSON file (optional)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for synthesis result"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test suite"
    )
    
    args = parser.parse_args()
    
    # Run tests if requested
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Load results
    results = []
    
    if args.results:
        for filepath in args.results:
            result = load_result_file(filepath)
            if result:
                results.append(result)
    
    if args.directory:
        dir_results = load_results_from_directory(args.directory, args.pattern)
        results.extend(dir_results)
    
    if not results:
        print("Error: No results to synthesize", file=sys.stderr)
        print("Use --results file1.json file2.json or --directory /path/to/results")
        sys.exit(1)
    
    # Load original task if provided
    original_task = None
    if args.original_task:
        original_task = load_result_file(args.original_task)
    
    # Perform synthesis
    synthesis = synthesize_results(results, original_task)
    
    # Output result
    if args.json:
        print(json.dumps(synthesis, indent=2))
    else:
        print_synthesis_result(synthesis, verbose=args.verbose)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(synthesis, f, indent=2)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
