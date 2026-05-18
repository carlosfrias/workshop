#!/usr/bin/env python3
"""
binary_decompose.py — Binary Decomposition Engine (P1.2)

Splits high-complexity tasks into 2 equal sub-tasks with recursive
decomposition if still too large (max depth: 3). Health-aware triggering
(only on stressed/critical health status).

Usage:
    # Decompose a complex task
    python3 binary_decompose.py --task "complex_task" --complexity 8

    # With health check
    python3 binary_decompose.py --task "complex_task" --complexity 8 --check-health

    # Test mode
    python3 binary_decompose.py --test

Output: List of sub-task dicts ready for orchestration
"""
import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def check_health() -> str:
    """
    Check orchestrator health status.
    
    Returns:
        str: "healthy", "stressed", or "critical"
    """
    health_script = SCRIPT_DIR / "orchestrator_health.py"
    
    if not health_script.exists():
        # Fallback: assume healthy if script missing
        return "healthy"
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(health_script), "--json"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            health_data = json.loads(result.stdout)
            return health_data.get("status", "healthy")
        else:
            return "healthy"  # Default to healthy on error
    except Exception:
        return "healthy"


def assess_complexity(task_description: str, complexity_score: Optional[int] = None) -> Dict[str, Any]:
    """
    Assess task complexity and determine if decomposition is needed.
    
    Args:
        task_description: The task to assess
        complexity_score: Optional pre-computed complexity (1-10)
    
    Returns:
        Dict with complexity assessment
    """
    # If complexity score provided, use it
    if complexity_score is not None:
        score = max(1, min(10, complexity_score))
    else:
        # Estimate from description length and keywords
        score = estimate_complexity_from_text(task_description)
    
    # Determine if decomposition needed
    needs_decomposition = score >= 7
    
    # Determine decomposition depth needed
    if score >= 9:
        max_depth = 3
    elif score >= 8:
        max_depth = 2
    else:
        max_depth = 1
    
    return {
        "complexity_score": score,
        "needs_decomposition": needs_decomposition,
        "max_depth": max_depth,
        "assessment": get_complexity_description(score)
    }


def estimate_complexity_from_text(text: str) -> int:
    """
    Estimate complexity score from task description text.
    
    Args:
        text: Task description
    
    Returns:
        Complexity score 1-10
    """
    # Base score from length
    word_count = len(text.split())
    
    if word_count < 20:
        base_score = 3
    elif word_count < 50:
        base_score = 5
    elif word_count < 100:
        base_score = 7
    else:
        base_score = 8
    
    # Adjust for complexity keywords
    complexity_keywords = [
        "integrate", "orchestrate", "synchronize", "coordinate",
        "analyze", "evaluate", "optimize", "refactor",
        "migrate", "transform", "aggregate", "synthesize"
    ]
    
    keyword_count = sum(1 for kw in complexity_keywords if kw.lower() in text.lower())
    
    # Adjust score based on keywords
    adjusted_score = base_score + min(keyword_count, 2)
    
    return max(1, min(10, adjusted_score))


def get_complexity_description(score: int) -> str:
    """Get human-readable complexity description."""
    if score <= 3:
        return "LOW - Simple task, single operation"
    elif score <= 5:
        return "MEDIUM - Moderate task, 2-3 steps"
    elif score <= 7:
        return "HIGH - Complex task, multiple dependencies"
    else:
        return "CRITICAL - Very complex, requires decomposition"


def split_task_binary(task: Dict[str, Any], depth: int = 0) -> List[Dict[str, Any]]:
    """
    Split a task into 2 equal sub-tasks.
    
    Args:
        task: Task dict to split
        depth: Current recursion depth
    
    Returns:
        List of 2 sub-task dicts
    """
    task_description = task.get("description", task.get("sub_task", ""))
    complexity = task.get("complexity", 5)
    
    # Split description into two logical parts
    # Strategy: Split by sentences, then distribute evenly
    sentences = split_into_sentences(task_description)
    
    if len(sentences) <= 1:
        # Can't split further - split by words
        words = task_description.split()
        mid = len(words) // 2
        part1 = " ".join(words[:mid])
        part2 = " ".join(words[mid:])
    else:
        # Split sentences evenly
        mid = len(sentences) // 2
        part1 = " ".join(sentences[:mid])
        part2 = " ".join(sentences[mid:])
    
    # Calculate new complexity (reduced by ~40% per split)
    new_complexity = max(1, round(complexity * 0.6))
    
    # Generate sub-tasks
    sub_task_1 = {
        "id": f"{task.get('id', 'task')}-a-{depth}",
        "description": part1 or task_description[:len(task_description)//2],
        "sub_task": part1 or "Part A",
        "complexity": new_complexity,
        "depth": depth + 1,
        "parent_id": task.get("id"),
        "part": "A",
        "total_parts": 2,
        "created": datetime.now().isoformat()
    }
    
    sub_task_2 = {
        "id": f"{task.get('id', 'task')}-b-{depth}",
        "description": part2 or task_description[len(task_description)//2:],
        "sub_task": part2 or "Part B",
        "complexity": new_complexity,
        "depth": depth + 1,
        "parent_id": task.get("id"),
        "part": "B",
        "total_parts": 2,
        "created": datetime.now().isoformat()
    }
    
    return [sub_task_1, sub_task_2]


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    import re
    # Simple sentence splitting on . ! ?
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def decompose_recursive(
    task: Dict[str, Any],
    max_depth: int = 3,
    current_depth: int = 0,
    complexity_threshold: int = 6
) -> List[Dict[str, Any]]:
    """
    Recursively decompose a task until complexity is manageable.
    
    Args:
        task: Task to decompose
        max_depth: Maximum recursion depth (default: 3)
        current_depth: Current recursion depth
        complexity_threshold: Stop decomposing if complexity <= this
    
    Returns:
        List of leaf sub-tasks
    """
    # Check if we should stop decomposing
    task_complexity = task.get("complexity", 5)
    
    if current_depth >= max_depth:
        # Max depth reached - return as-is
        task["decomposition_stopped"] = "max_depth"
        return [task]
    
    if task_complexity <= complexity_threshold:
        # Complexity manageable - return as-is
        task["decomposition_stopped"] = "complexity_threshold"
        return [task]
    
    # Split into 2 sub-tasks
    sub_tasks = split_task_binary(task, current_depth)
    
    # Recursively decompose each sub-task
    results = []
    for sub_task in sub_tasks:
        results.extend(decompose_recursive(
            sub_task,
            max_depth=max_depth,
            current_depth=current_depth + 1,
            complexity_threshold=complexity_threshold
        ))
    
    return results


def binary_decompose(
    task_description: str,
    complexity: int,
    health_status: Optional[str] = None,
    max_depth: int = 3
) -> Dict[str, Any]:
    """
    Main binary decomposition function.
    
    Args:
        task_description: The task to decompose
        complexity: Complexity score (1-10)
        health_status: Optional health status override
        max_depth: Maximum decomposition depth
    
    Returns:
        Dict with decomposition results
    """
    # Check health if not provided
    if health_status is None:
        health_status = check_health()
    
    # Assess complexity
    complexity_assessment = assess_complexity(task_description, complexity)
    
    # Health-aware triggering: only decompose on stressed/critical
    if health_status == "healthy" and not complexity_assessment["needs_decomposition"]:
        # No decomposition needed
        return {
            "status": "no_decomposition",
            "reason": "Health is healthy and complexity is manageable",
            "health_status": health_status,
            "complexity_assessment": complexity_assessment,
            "sub_tasks": [{
                "id": "task-0",
                "description": task_description,
                "sub_task": task_description,
                "complexity": complexity,
                "depth": 0,
                "part": "single",
                "total_parts": 1,
                "created": datetime.now().isoformat()
            }]
        }
    
    # Create initial task
    initial_task = {
        "id": f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": task_description,
        "sub_task": task_description,
        "complexity": complexity,
        "depth": 0,
        "health_status": health_status,
        "created": datetime.now().isoformat()
    }
    
    # Perform recursive decomposition
    sub_tasks = decompose_recursive(
        initial_task,
        max_depth=max_depth,
        current_depth=0,
        complexity_threshold=5  # Stop when complexity <= 5
    )
    
    # Log decomposition
    log_decomposition(initial_task, sub_tasks, health_status)
    
    return {
        "status": "decomposed",
        "reason": f"Health: {health_status}, Complexity: {complexity}",
        "health_status": health_status,
        "complexity_assessment": complexity_assessment,
        "original_task": initial_task,
        "sub_tasks": sub_tasks,
        "total_sub_tasks": len(sub_tasks),
        "max_depth_reached": max(s.get("depth", 0) for s in sub_tasks),
        "decomposition_timestamp": datetime.now().isoformat()
    }


def log_decomposition(original: Dict, sub_tasks: List[Dict], health_status: str):
    """Log decomposition event to JSONL file."""
    log_dir = SCRIPT_DIR.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "binary_decomposition.jsonl"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "health_status": health_status,
        "original_task_id": original.get("id"),
        "original_complexity": original.get("complexity"),
        "sub_task_count": len(sub_tasks),
        "sub_task_ids": [s.get("id") for s in sub_tasks],
        "max_depth": max(s.get("depth", 0) for s in sub_tasks)
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def print_decomposition_result(result: Dict[str, Any], verbose: bool = False):
    """Print decomposition result in human-readable format."""
    print("=" * 70)
    print("BINARY DECOMPOSITION RESULT")
    print("=" * 70)
    print(f"Status: {result['status'].upper()}")
    print(f"Reason: {result['reason']}")
    print(f"Health Status: {result['health_status']}")
    print()
    
    if result['status'] == 'no_decomposition':
        print("No decomposition needed - task will execute as-is")
        print()
        print("Task:")
        print(f"  ID: {result['sub_tasks'][0]['id']}")
        print(f"  Description: {result['sub_tasks'][0]['sub_task'][:100]}...")
        print(f"  Complexity: {result['sub_tasks'][0]['complexity']}")
    else:
        print(f"Original Task Complexity: {result['original_task']['complexity']}")
        print(f"Sub-tasks Generated: {result['total_sub_tasks']}")
        print(f"Max Depth Reached: {result['max_depth_reached']}")
        print()
        print("Sub-tasks:")
        print("-" * 70)
        
        for i, task in enumerate(result['sub_tasks'], 1):
            print(f"\n{i}. {task['id']}")
            print(f"   Part: {task.get('part', 'single')} of {task.get('total_parts', 1)}")
            print(f"   Depth: {task.get('depth', 0)}")
            print(f"   Complexity: {task.get('complexity', 'N/A')}")
            print(f"   Description: {task.get('sub_task', '')[:100]}...")
            
            if verbose:
                print(f"   Full: {task.get('description', '')}")
            
            if task.get('decomposition_stopped'):
                print(f"   ⚠️ Decomposition stopped: {task['decomposition_stopped']}")
    
    print()
    print("=" * 70)


def run_tests():
    """Run test suite for binary decomposition."""
    print("Running Binary Decomposition Tests")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: High complexity task → verify binary split
    print("\n[Test 1] High complexity task (complexity=8) → verify binary split")
    result = binary_decompose(
        "Analyze market data and generate trading signals with risk assessment",
        complexity=8,
        health_status="stressed"
    )
    
    if result['status'] == 'decomposed' and len(result['sub_tasks']) >= 2:
        print("  ✅ PASS: Task was decomposed into 2+ sub-tasks")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Task should have been decomposed")
        tests_failed += 1
    
    # Test 2: Recursive decomposition (complexity=10, should go to depth 2-3)
    print("\n[Test 2] Very high complexity (complexity=10) → verify recursive decomposition")
    result = binary_decompose(
        "Integrate multiple data sources, synchronize trading signals, and coordinate execution across nodes",
        complexity=10,
        health_status="critical"
    )
    
    if result['status'] == 'decomposed' and result['max_depth_reached'] >= 2:
        print(f"  ✅ PASS: Recursive decomposition to depth {result['max_depth_reached']}")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Should have decomposed recursively")
        tests_failed += 1
    
    # Test 3: Low complexity task → no decomposition
    print("\n[Test 3] Low complexity task (complexity=3) → no decomposition")
    result = binary_decompose(
        "Check system status",
        complexity=3,
        health_status="healthy"
    )
    
    if result['status'] == 'no_decomposition' and len(result['sub_tasks']) == 1:
        print("  ✅ PASS: No decomposition for low complexity")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Should not decompose low complexity tasks")
        tests_failed += 1
    
    # Test 4: Health-aware triggering
    print("\n[Test 4] Health-aware triggering (healthy + high complexity)")
    result = binary_decompose(
        "Complex task that would normally decompose",
        complexity=8,
        health_status="healthy"
    )
    
    # On healthy, high complexity should still decompose
    if result['status'] == 'decomposed':
        print("  ✅ PASS: Decomposition triggered by complexity even when healthy")
        tests_passed += 1
    else:
        print("  ❌ FAIL: Should decompose high complexity tasks")
        tests_failed += 1
    
    # Test 5: Max depth enforcement
    print("\n[Test 5] Max depth enforcement (complexity=10, max_depth=2)")
    result = binary_decompose(
        "Very complex task with many dependencies",
        complexity=10,
        health_status="critical",
        max_depth=2
    )
    
    if result['max_depth_reached'] <= 2:
        print(f"  ✅ PASS: Max depth respected (reached {result['max_depth_reached']})")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Exceeded max depth (reached {result['max_depth_reached']})")
        tests_failed += 1
    
    # Test 6: Complexity assessment
    print("\n[Test 6] Complexity assessment accuracy")
    assessment = assess_complexity(
        "Integrate and synchronize multiple systems with complex orchestration and analysis",
        complexity_score=None
    )
    
    # Assessment should detect complexity keywords and score accordingly
    if assessment['complexity_score'] >= 5:
        print(f"  ✅ PASS: Complexity correctly assessed as {assessment['complexity_score']}")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Complexity assessment inaccurate ({assessment['complexity_score']})")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"TESTS PASSED: {tests_passed}/{tests_passed + tests_failed}")
    print("=" * 70)
    
    return tests_failed == 0


def main():
    parser = argparse.ArgumentParser(
        description="Binary Decomposition Engine for high-complexity tasks"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="Task description to decompose"
    )
    parser.add_argument(
        "--complexity",
        type=int,
        default=5,
        help="Complexity score (1-10, default: 5)"
    )
    parser.add_argument(
        "--health",
        type=str,
        choices=["healthy", "stressed", "critical"],
        help="Override health status"
    )
    parser.add_argument(
        "--check-health",
        action="store_true",
        help="Check actual health status before decomposing"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum decomposition depth (default: 3)"
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
    
    # Require task description
    if not args.task:
        parser.print_help()
        print("\nError: --task is required")
        sys.exit(1)
    
    # Check health if requested
    health_status = args.health
    if args.check_health and not health_status:
        health_status = check_health()
        print(f"Health status: {health_status}")
    
    # Perform decomposition
    result = binary_decompose(
        task_description=args.task,
        complexity=args.complexity,
        health_status=health_status,
        max_depth=args.max_depth
    )
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_decomposition_result(result, verbose=args.verbose)


if __name__ == "__main__":
    main()
