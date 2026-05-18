# Module 6: Hardware Specifications

**Version:** 1.0  
**Tokens:** ~140  
**Load Trigger:** User asks "hardware", "specs", "requirements", "resources", "CPU", "RAM"  
**Unload:** After response sent

---

## Minimum Requirements

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | {cores} @ {speed} | {Workload type} |
| **RAM** | {GB} | {Memory-intensive operations} |
| **Storage** | {GB} {type} | {Storage type: SSD/HDD} |
| **Network** | {speed} | {Network-intensive operations} |

**Example:**

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | 4 cores @ 2.5 GHz | Container orchestration |
| **RAM** | 8 GB | Model loading + application |
| **Storage** | 20 GB SSD | Container images + logs |
| **Network** | 1 Gbps | Image pull + health checks |

---

## Recommended Specifications

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | {cores} @ {speed} | {Optimal performance} |
| **RAM** | {GB} | {Headroom for spikes} |
| **Storage** | {GB} {type} | {Faster I/O} |
| **Network** | {speed} | {Redundancy} |

**Example:**

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | 8 cores @ 3.0 GHz | Optimal performance |
| **RAM** | 16 GB | Headroom for spikes |
| **Storage** | 50 GB NVMe SSD | Faster I/O |
| **Network** | 10 Gbps | Redundancy |

---

## Load Characteristics

| Load Type | Level | Description |
|-----------|-------|-------------|
| **CPU Load** | {Low/Medium/High} | {Description of CPU-intensive tasks} |
| **Memory Load** | {Low/Medium/High} | {Description of memory usage patterns} |
| **I/O Load** | {Low/Medium/High} | {Description of disk/network I/O} |

**Example:**

| Load Type | Level | Description |
|-----------|-------|-------------|
| **CPU Load** | Medium | Container orchestration, health checks |
| **Memory Load** | Medium | Model loading (2-4 GB), application state |
| **I/O Load** | Low | Occasional image pull, log writes |

---

## Scaling Recommendations

| Scaling Type | When to Apply | How to Scale |
|--------------|---------------|--------------|
| **Vertical** | {Condition} | {Action} |
| **Horizontal** | {Condition} | {Action} |

**Example:**

| Scaling Type | When to Apply | How to Scale |
|--------------|---------------|--------------|
| **Vertical** | Memory >80% consistently | Add RAM (8GB → 16GB) |
| **Horizontal** | CPU >70% for >5 min | Add additional node |

---

## Compatible Nodes

| Node | Specs | Performance | Recommendation |
|------|-------|-------------|----------------|
| {node} | {specs} | {rating} | {Recommended/Not Recommended} |

**Example:**

| Node | Specs | Performance | Recommendation |
|------|-------|-------------|----------------|
| fnet3 | 31GB RAM, i7 | ⭐⭐⭐⭐⭐ | ✅ Recommended |
| fnet4 | 31GB RAM, i7 | ⭐⭐⭐⭐⭐ | ✅ Recommended |
| fnet5 | 15GB RAM, i5 | ⭐⭐⭐ | ⚠️ Acceptable |
| fnet6 | 15GB RAM, i5 | ⭐⭐⭐ | ⚠️ Acceptable |
| fnet7 | 8GB RAM, i3 | ⭐⭐ | ❌ Not Recommended |

---

## Performance by Hardware Tier

| Tier | CPU | RAM | Expected Time | Cost |
|------|-----|-----|---------------|------|
| **High** | 8+ cores | 32GB | 8-12s | $0.018/hr |
| **Medium** | 4-8 cores | 16GB | 12-18s | $0.012/hr |
| **Low** | 2-4 cores | 8GB | 18-30s | $0.006/hr |

---

## Hardware Health Check

```bash
# Check hardware status
python3 technical-infrastructure/scripts/check-hardware.py \
  --cpu --memory --storage --network
```

**Thresholds:**

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| CPU Usage | <50% | 50-80% | >80% |
| Memory Usage | <75% | 75-90% | >90% |
| Storage Free | >20% | 10-20% | <10% |

---

## Questions This Module Answers

- ✅ "What hardware is needed for {playbook}?"
- ✅ "What are the requirements for {playbook}?"
- ✅ "Can {node} run {playbook}?"
- ✅ "How much RAM does {playbook} need?"

---

## Questions This Module Does NOT Answer

- ❌ "What does {playbook} do?" → Load Module 1
- ❌ "What does {playbook} depend on?" → Load Module 2
- ❌ "What data does {playbook} use?" → Load Module 3
- ❌ "When should {playbook} run?" → Load Module 4
- ❌ "How long does {playbook} take?" → Load Module 5

---

**Module End**

*Return to core prompt after use*
