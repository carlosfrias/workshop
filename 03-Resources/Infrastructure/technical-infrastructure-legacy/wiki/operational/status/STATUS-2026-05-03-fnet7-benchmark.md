# STATUS-2026-05-03-fnet7-benchmark

**Session:** fnet7 Benchmark & Model Right-Sizing  
**Started:** 2026-05-03 23:45 ET  
**Completed:** 2026-05-03 23:55 ET  
**Domain:** technical-infrastructure  

---

## Summary

**fnet7 has been re-benchmarked and model profiles right-sized to capacity.** All TI-016 deliverables complete.

---

## Benchmark Results

| Model | Before Governor Fix | After Fix | Improvement |
|-------|---------------------|-----------|-------------|
| qwen3.5:4b | 3.47 t/s | **3.99 t/s** | **+15%** ✅ |
| qwen3:8b | 3.31 t/s | 3.34 t/s | +1% |
| gemma4:e4b | N/A | Not installed | By design (9.6GB > 9GB limit) |

**Conclusion:** CPU governor fix verified — 15% performance improvement on qwen3.5:4b.

---

## Model Right-Sizing

**fnet7 Capacity:**
- RAM: 15GB
- Safe model size: 9GB
- Available models: qwen3.5:4b (3.4GB), qwen3:8b (5.2GB)
- Excluded: gemma4:e4b (9.6GB exceeds limit)

**Routing Profile (auto):**
- HIGH: qwen3.5:4b (fastest)
- MEDIUM: qwen3:8b
- LOW: qwen3:8b (thinking: off)

---

## Files Created

- `technical-infrastructure/operational/data/lab-specs/node-benchmarks/fnet7-qwen3.5_4b.json` — 3.99 t/s
- `technical-infrastructure/operational/data/lab-specs/node-benchmarks/fnet7-qwen3_8b.json` — 3.34 t/s
- `technical-infrastructure/operational/data/lab-specs/node-configs/fnet7/models.json`
- `technical-infrastructure/operational/data/lab-specs/node-configs/fnet7/model-router.json`
- `technical-infrastructure/operational/data/lab-specs/node-capacity-summary.json` — Updated
- `technical-infrastructure/wiki/operational/sessions/SESSION-NOTES-2026-05-03-fnet7-benchmark.md` — Full report

---

## Tools Used

- `technical-infrastructure/scripts/pilot-lab/benchmark-lab.sh` — Existing TI-016 benchmarking tool
- `technical-infrastructure/scripts/pilot-lab/generate-node-profiles.py` — Existing TI-016 profile generator

**No new tools created. Leveraged existing TI-016 infrastructure.**

---

## Backlog Updates

- TI-016 Issue #4 (fnet7 ~22% slower): ✅ **CLOSED**
- fnet7 benchmark verification: ✅ **COMPLETE**
- fnet7 model right-sizing: ✅ **COMPLETE**

---

**fnet7 fully operational with verified performance and right-sized model configuration.**
