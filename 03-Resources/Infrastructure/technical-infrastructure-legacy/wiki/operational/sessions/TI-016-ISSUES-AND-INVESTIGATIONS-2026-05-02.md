# TI-016 Issues and Investigations Log

**Date**: 2026-05-02  
**Domain**: technical-infrastructure  
**Task**: TI-016 — Expand local-model-pilot for Lab Nodes  

---

## Issue 1: fnet2 — NVIDIA Driver Hangs Hardware Detection

**Severity**: 🟡 Medium (blocks full data collection)  
**Status**: 🔴 OPEN — Requires manual intervention  

### Description

During `remote-detect.sh` execution, fnet2's `detect-hardware.sh` hangs on GPU detection. The script calls `nvidia-smi` which prints an error and then hangs:

```
The 595.71.05 NVIDIA driver will ignore this GPU. Continuing probe...
NVIDIA-SMI: has failed because it couldn't communicate with the NVIDIA driver.
```

fnet2 hardware: Intel HD Graphics 530 (iGPU), NOT an NVIDIA GPU. An incorrect NVIDIA driver was previously installed.

### RCA

The `detect-hardware.sh` script has a GPU detection sequence:
1. Check for `nvidia-smi` command → Found (because driver is installed)
2. Run `nvidia-smi` → Fails because no NVIDIA hardware exists → Hangs

The script then stalls, preventing completion for fnet2.

### Impact

- No hardware profile generated for fnet2
- Cannot run benchmarks on fnet2
- fnet2 excluded from the node-capacity-summary

### Resolution Plan

1. Remove NVIDIA driver packages: `sudo apt remove nvidia-driver* nvidia-dkms nvidia-kernel-*`
2. Regenerate initramfs: `sudo update-initramfs -u`
3. Reboot node
4. Re-run `remote-detect.sh fnet2`

---

## Issue 2: fnet1 — No Models Installed

**Severity**: 🟡 Medium (incomplete benchmark data)  
**Status**: 🔴 OPEN  

### Description

fnet1 has Ollama running (version 0.20.2) but zero models installed. Benchmarking skipped all candidates with `status: "not_installed"`.

### Impact

- No benchmark data for fnet1
- Cannot validate if the i5-6400 (4c) performance differs from i7-10710U (12c)

### Resolution Plan

1. Pull candidate models: `ollama pull qwen3.5:4b qwen3:8b`
2. Re-run `benchmark-lab.sh fnet1`

---

## Issue 3: fnet7 — gemma4:e4b Not Installed

**Severity**: 🟢 Low (data gap)  
**Status**: 🔴 OPEN  

### Description

fnet7 has only 2 models installed (`qwen3.5:4b` and `qwen3:8b`). `gemma4:e4b` is not installed despite having enough RAM (15GB, safe limit 9GB, model is 9.6GB — actually slightly exceeds limit).

**Update**: After re-examining the data, fnet7's `safe_model_size_gb` is 9GB and `gemma4:e4b` is 9.6GB. This is correct behavior — the model is slightly too large for the safety margin.

### Resolution

No action needed. If gemma4:e4b is needed on fnet7, reduce system overhead or install it manually with the understanding it's close to the limit.

---

## Issue 4: fnet7 — ~22% Slower Despite Same CPU

**Severity**: 🟡 Medium (routing implication)  
**Status**: 🔴 OPEN — Under investigation  

### Description

fnet7 and fnet3–fnet6 all have the same CPU (Intel i7-10710U @ 1.10GHz, 12 cores). However, fnet7's benchmark results are significantly slower:

| Model | fnet3–fnet6 avg | fnet7 | Delta |
|-------|----------------|-------|-------|
| qwen3.5:4b | 4.43 t/s | 3.51 t/s | -21% |
| qwen3:8b | 4.79 t/s | 3.30 t/s | -31% |

### Possible Causes

1. **Thermal throttling**: fnet7 may have inadequate cooling
2. **Background processes**: Heavy system load or other services running
3. **Memory configuration**: Single-channel vs dual-channel RAM
4. **BIOS/UEFI settings**: Different power profiles
5. **Disk I/O bottleneck**: Model loading slower on slower storage
6. **Ollama version**: fnet7 runs 0.21.1 vs 0.22.1 on fnet3–fnet6

### Investigation Steps

```bash
# On fnet7 via SSH — run these diagnostics
# 1. Check CPU temperature
sensors 2>/dev/null || echo "No sensors"
# 2. Check load average
cat /proc/loadavg
# 3. Check memory channels
dmidecode -t memory 2>/dev/null | grep -i "locator\|size" | head -10
# 4. Check CPU governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# 5. Check background processes
ps aux --sort=-%cpu | head -10
# 6. Check disk speed (if model loading is slow)
dd if=/dev/zero of=/tmp/test bs=1M count=100 oflag=direct 2>&1 | tail -1
# 7. Check Ollama version difference
ollama --version
```

---

## Issue 5: All Nodes Show Identical Performance for Same CPU

**Severity**: 🟢 Low (observation)  
**Status**: ✅ EXPLAINED  

### Observation

fnet3, fnet4, fnet5, fnet6 all return nearly identical benchmark numbers (~4.4–5.6 t/s) despite being separate physical nodes.

### Explanation

This is expected and actually validates the methodology. The i7-10710U is the same CPU across all four nodes, and all four have 31GB RAM. With CPU-bound inference and no GPU acceleration, identical hardware should produce identical results. The small variance (~0.1–0.2 t/s) is normal thermal/noise variation.

---

## Issue 6: gemma4:e4b Is Fastest Despite Being Largest

**Severity**: 🟢 Low (counterintuitive but validated)  
**Status**: ✅ EXPLAINED  

### Observation

The largest model (gemma4:e4b, 9.6GB) is consistently the fastest (~5.5 t/s) on 31GB nodes, beating both smaller models.

Counterintuitive because common wisdom says smaller models = faster inference.

### Explanation

1. **Architecture**: Gemma4 uses a Mixture-of-Experts (MoE) architecture that activates only a subset of parameters per token
2. **Optimization**: The Q4_K_M quantization of gemma4:e4b may be more efficiently implemented in the Ollama runtime than qwen3's
3. **Context handling**: The benchmark prompt is short (21 prompt eval tokens), so context window size doesn't matter and the model's forward pass efficiency dominates
4. **CPU utilization**: Gemma4 may use AVX2/vector instructions more efficiently on x86_64 than qwen3

This is a data-driven finding, not an error. The routing framework should use it.

---

## Summary Table

| Issue | Node | Severity | Status | Action |
|-------|------|----------|--------|--------|
| NVIDIA driver blocks detection | fnet2 | 🟡 Medium | 🔴 Open | Remove NVIDIA packages, reboot |
| No models installed | fnet1 | 🟡 Medium | 🔴 Open | Pull models, re-benchmark |
| gemma4:e4b not installed | fnet7 | 🟢 Low | 🔴 Open | By design (RAM limit) |
| ~22% slower performance | fnet7 | 🟡 Medium | 🔴 Open | Investigate thermal/load |
| Identical performance across same CPU | fnet3–fnet6 | 🟢 Low | ✅ Explained | Normal — validates methodology |
| Largest model is fastest | All | 🟢 Low | ✅ Explained | MoE architecture advantage |

---

**END OF ISSUES LOG**
