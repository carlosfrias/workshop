# 📍 Plan Location Guide — Integrated Health Monitoring

> **📍 Navigation**  
> **Parent:** [Technical Infrastructure Wiki](../../WIKI.md) | [Technical Infrastructure Docs](./)  
> **Related:** [Unified Health Monitoring](./unified-health-monitoring.md) | [Master Playbook Prompt](./master-playbook-prompt.md) | [Backlog](/operational/BACKLOG.md)  
> **Quick Links:** [Master Plan](./unified-health-monitoring.md) | [TI-032 Backlog](/operational/BACKLOG.md#ti-032) | [Research Citations](../../operational/planning/RESEARCH-CITATIONS-MASTER-PROMPT.md)

---

**Created:** 2026-05-05  
**Purpose:** Quick reference for finding the integrated plan and related documents

---

## 🎯 Primary Plan Location

### **Unified Health Monitoring Master Plan**

**File:** `technical-infrastructure/wiki/technical-infrastructure/unified-health-monitoring.md`

**Wiki URL:** `/technical-infrastructure/technical-infrastructure/unified-health-monitoring`

**Contents:**
- ✅ Merged TI-031 Health Monitoring Protocol
- ✅ Merged Master Prompt Monitoring
- ✅ Merged ASSESSMENT-TI031-MASTER-PROMPT-GAPS (all 8 gaps addressed)
- ✅ Unified architecture with single decision tree
- ✅ 3-phase implementation plan (P0: 5h, P1: 7h, P2: 4h)
- ✅ File structure and success criteria

---

## 📦 Superseded Documents (Archived)

| Document | Previous Location | Status | Action |
|----------|------------------|--------|--------|
| **PLAN-TI031-INTEGRATION-v1.0.md** | `technical-infrastructure/operational/planning/` | 📦 SUPERSEDED | Refer to unified plan |
| **ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md** | `technical-infrastructure/operational/planning/` | 📦 SUPERSEDED | Refer to unified plan |

**Note:** Both documents now have redirect notices at the top pointing to the unified plan.

---

## 📋 Backlog Items

### Active

| ID | Item | Priority | Status | Location |
|----|------|----------|--------|----------|
| **TI-032** | Integrated Health-Aware Playbook Monitoring System | 🔴 CRITICAL | 📋 PENDING REVIEW | [BACKLOG.md](technical-infrastructure/wiki/operational/BACKLOG.md#ti-032) |

### Superseded

| ID | Item | Priority | Status | Location |
|----|------|----------|--------|----------|
| **TI-PLAYBOOK-MASTER** | Master Prompt for Playbook Keyword System | 🟡 MEDIUM | 🔄 SUPERSEDED by TI-032 | [BACKLOG.md](technical-infrastructure/wiki/operational/BACKLOG.md#ti-playbook-master) |

---

## 📁 Complete File Map

```
wiki/
├── index.md                                    ← Updated with unified plan link
└── technical-infrastructure/
    ├── unified-health-monitoring.md            🆕 MASTER PLAN (this is the one)
    ├── master-playbook-prompt.md              🔄 Referenced by unified plan
    ├── orchestration-status-monitor.md        🔄 Referenced by unified plan
    └── low-capacity-model-validation.md       🔄 Referenced by unified plan

technical-infrastructure/
├── operational/
│   ├── BACKLOG.md                             ← TI-032 added, TI-PLAYBOOK-MASTER superseded
│   └── planning/
│       ├── PLAN-TI031-INTEGRATION-v1.0.md     📦 SUPERSEDED (redirect notice)
│       ├── ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md  📦 SUPERSEDED (redirect notice)
│       └── IMPLEMENTATION-SUMMARY-2026-05-05-PLAYBOOK-KEYWORD-SYSTEM.md  ✅ Reference
```

---

## 🔗 Quick Access

### To View the Plan:
1. **Wiki:** Navigate to `Technical Infrastructure → Unified Health Monitoring`
2. **File:** Open `technical-infrastructure/wiki/technical-infrastructure/unified-health-monitoring.md`
3. **Direct:** [Click here](/technical-infrastructure/technical-infrastructure/unified-health-monitoring)

### To View Backlog:
1. **Wiki:** Navigate to `Operations → Technical Infrastructure Backlog`
2. **File:** Open `technical-infrastructure/wiki/operational/BACKLOG.md`
3. **Search for:** `TI-032`

### To View Superseded Items:
- **TI-PLAYBOOK-MASTER:** Search `BACKLOG.md` for `TI-PLAYBOOK-MASTER`
- **PLAN-TI031-INTEGRATION:** Open file (has redirect notice)
- **ASSESSMENT-TI031-GAPS:** Open file (has redirect notice)

---

## ✅ What's Changed

### Before (Separate Plans)
- TI-031: Health monitoring for orchestrator only
- Master Prompt: Playbook monitoring only
- Gap Analysis: Documented problems, no solutions
- 3 separate documents, no coordination

### After (Unified Plan)
- **Single plan** covering orchestrator + lab nodes + playbooks
- **Single decision engine** for all routing decisions
- **Single implementation timeline** (16 hours total)
- **Single success criteria** set
- All 8 gaps from assessment addressed

---

## 🎯 Next Steps

1. **Review the unified plan** at the location above
2. **Approve or request changes** to the 3-phase implementation
3. **Begin Phase 0** (P0: 5 hours) upon approval
4. **Track progress** via TI-032 backlog item

---

**Questions?** Refer to the unified plan document or the TI-032 backlog item for full details.
