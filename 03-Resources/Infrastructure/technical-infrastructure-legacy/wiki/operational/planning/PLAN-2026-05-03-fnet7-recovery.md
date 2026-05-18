# fnet7 Recovery Plan

**Created:** 2026-05-03  
**Priority:** 🔴 High (blocks reliable task execution on 1/7 lab nodes)  
**Status:** 🔄 In Progress  

---

## Problem Statement

fnet7 (Intel i7-10710U, 15GB RAM) is the slowest node in the lab despite having the same CPU as fnet3-fnet6:

| Model | fnet3-fnet6 avg | fnet7 | Delta |
|-------|----------------|-------|-------|
| qwen3.5:4b | 4.43 t/s | 3.47 t/s | **-22%** |
| qwen3:8b | 4.79 t/s | 3.31 t/s | **-31%** |

Additionally, task verification tasks are stuck in `running/` state, indicating a task worker issue.

---

## Root Causes Identified

### 1. CPU Governor: `powersave` (Confirmed)
**Impact:** 22-31% performance loss  
**Evidence:** TI-016 investigation log, STATUS-2026-05-02-2145  
**Fix Applied:** Governor changed to `performance`, cpufrequtils installed  
**Verification:** ❌ PENDING (task stuck)

### 2. Task Worker Timer Issue
**Impact:** Cannot verify fixes via TI-009 task system  
**Evidence:** Task `4dd77270` remained in `running/` after timer should have fired  
**Possible Causes:**
- systemd timer not firing
- Task worker script error
- Permission issue on `/srv/tasks/running/`

### 3. Ollama Version Lag
**Impact:** Potential performance/compatibility issues  
**Evidence:** fnet7 runs 0.21.1, fnet3-fnet6 run 0.22.1  
**Fix:** Update to 0.22.1

---

## Execution Plan

### Phase 1: Direct SSH Diagnostics (15 min)
```bash
# 1. Check CPU governor
ssh fnet7 "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"

# 2. Check cpufrequtils service
ssh fnet7 "systemctl status cpufrequtils --no-pager"

# 3. Check task worker status
ssh fnet7 "systemctl status gist-worker@1 --no-pager"
ssh fnet7 "ls -la /srv/tasks/{pending,running,completed}/"

# 4. Check Ollama version
ssh fnet7 "ollama --version"

# 5. Check system load
ssh fnet7 "cat /proc/loadavg && ps aux --sort=-%cpu | head -5"

# 6. Check thermal state
ssh fnet7 "sensors 2>/dev/null || echo 'No sensors'"
```

### Phase 2: CPU Governor Verification (10 min)
```bash
# If governor shows 'powersave', re-apply fix
ssh fnet7 << 'EOF'
sudo systemctl stop cpufrequtils
sudo sed -i 's/GOVERNOR=.*/GOVERNOR="performance"/' /etc/default/cpufrequtils
sudo systemctl start cpufrequtils
sudo systemctl enable cpufrequtils
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
EOF

# Quick benchmark
ssh fnet7 "time ollama run qwen3.5:4b 'Count 1 to 5' 2>&1 | tail -3"
```

### Phase 3: Task Worker Fix (15 min)
```bash
# Check timer status
ssh fnet7 "systemctl list-timers | grep gist"

# Check worker logs
ssh fnet7 "journalctl -u gist-worker@1 --since '30 min ago' --no-pager"

# Restart worker
ssh fnet7 "sudo systemctl restart gist-worker@1"

# Test with simple task
cat > /tmp/fnet7-test.json << 'EOF'
{
  "task_id": "fnet7-worker-test",
  "type": "shell",
  "node": "fnet7",
  "description": "Worker health check",
  "command": "echo 'Worker OK' && date",
  "timeout_seconds": 30
}
EOF
python3 technical-infrastructure/scripts/submit_task.py --node fnet7 --file /tmp/fnet7-test.json

# Monitor
watch -n 2 'ls /srv/tasks/*/fnet7-worker-test.json 2>/dev/null || echo "Task not found"'
```

### Phase 4: Ollama Update (10 min)
```bash
# Update Ollama
ssh fnet7 << 'EOF'
curl -fsSL https://ollama.com/install.sh | sudo bash
ollama --version
sudo systemctl restart ollama
EOF

# Verify models still present
ssh fnet7 "ollama list"
```

### Phase 5: Re-benchmark (10 min)
```bash
# Run official benchmark
python3 technical-infrastructure/scripts/pilot-lab/benchmark-lab.sh --nodes fnet7 --output-dir technical-infrastructure/operational/data/lab-specs/node-benchmarks/

# Or quick manual check
ssh fnet7 << 'EOF'
echo "qwen3.5:4b benchmark:"
time ollama run qwen3.5:4b 'Write a 3-sentence story about a robot learning to paint' 2>&1 | tail -5
echo "qwen3:8b benchmark:"
time ollama run qwen3:8b 'Write a 3-sentence story about a robot learning to paint' 2>&1 | tail -5
EOF
```

---

## Success Criteria

- [ ] CPU governor shows `performance` consistently
- [ ] Task worker completes tasks within 60 seconds
- [ ] Ollama version matches fnet3-fnet6 (0.22.1)
- [ ] qwen3.5:4b benchmark ≥ 4.0 t/s (was 3.47 t/s, target is ~4.4 t/s)
- [ ] qwen3:8b benchmark ≥ 4.3 t/s (was 3.31 t/s, target is ~4.8 t/s)

---

## Rollback Plan

If performance degrades after Ollama update:
```bash
ssh fnet7 "sudo ollama serve --stop && sudo apt remove ollama && sudo apt install ollama=0.21.1"
```

---

## Files to Update After Fix

- `technical-infrastructure/wiki/operational/status/STATUS-2026-05-03-{timestamp}.md`
- `technical-infrastructure/wiki/operational/sessions/SESSION-NOTES-2026-05-03-fnet7-recovery.md`
- `technical-infrastructure/operational/data/lab-specs/node-benchmarks/fnet7-*.json` (re-benchmark)
- `technical-infrastructure/wiki/operational/BACKLOG.md` (close TI-016 Issue #4)

---

**END OF PLAN**
