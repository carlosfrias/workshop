# Health Check Integration Guide

## Overview
Health checks ensure system stability before executing critical operations. This integration enforces thresholds for RAM (80%/92%), CPU (4.0/6.0), and 0 swap usage.

## Thresholds
- **Healthy**: RAM <80%, CPU <4.0, 0 swap
- **Stressed**: 80% ≤ RAM <92%, 4.0 ≤ CPU <6.0, 0 swap
- **Critical**: RAM ≥92%, CPU ≥6.0, or swap >0

## Integration Workflow
1. Pre-execution health check via `orchestrator_health.py`
2. JSON output with metrics and status
3. Status code 0/1/2 for health
4. Decision logging to health-decisions.jsonl

## Troubleshooting
- **Missing psutil**: `pip install psutil`
- **High memory**: Use `dd if=/dev/zero of=memory_testfile bs=1M count=1000` to simulate
- **Swap usage**: Check `/proc/swaps` and disable if unnecessary

## Example Output
```json
{
  "timestamp": 1683302400,
  "ram_percent": 95,
  "cpu_percent": 7.5,
  "swap_usage": 0,
  "status": "critical"
}
```