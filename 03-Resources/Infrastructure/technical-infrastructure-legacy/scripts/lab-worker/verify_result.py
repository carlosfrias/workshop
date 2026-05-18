#!/usr/bin/env python3
"""Verifier Agent
Checks task results for correctness, completeness, and format validity.
"""

import json
import sys
from pathlib import Path

def verify(result_path):
    """Verify a result file."""
    path = Path(result_path)
    if not path.exists():
        return {"status": "FAIL", "reason": "Result file not found"}
    
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return {"status": "FAIL", "reason": f"Invalid JSON: {e}"}
    
    checks = []
    
    # Check required fields
    if "response" in data:
        checks.append("✅ Has response field")
    else:
        checks.append("❌ Missing response field")
        return {"status": "FAIL", "reason": "Missing response", "checks": checks}
    
    if "done" in data and data["done"]:
        checks.append("✅ Inference completed")
    else:
        checks.append("❌ Incomplete inference")
        return {"status": "FAIL", "reason": "Incomplete", "checks": checks}
    
    # Check for empty response
    response = data.get("response", "").strip()
    if len(response) > 0:
        checks.append(f"✅ Non-empty response ({len(response)} chars)")
    else:
        checks.append("❌ Empty response")
        return {"status": "FAIL", "reason": "Empty response", "checks": checks}
    
    # Check response time was reasonable
    if "total_duration" in data:
        duration_ns = data["total_duration"]
        duration_s = duration_ns / 1e9
        if duration_s < 60:
            checks.append(f"✅ Good latency: {duration_s:.2f}s")
        else:
            checks.append(f"⚠️ Slow latency: {duration_s:.2f}s")
    
    return {"status": "PASS", "checks": checks, "response_preview": response[:100]}

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <result_file>")
        sys.exit(1)
    
    result = verify(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
