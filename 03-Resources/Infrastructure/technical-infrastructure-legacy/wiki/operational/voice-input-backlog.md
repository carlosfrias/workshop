# Voice Input Backlog

Tracking feature requests, bugs, and enhancements for the voice-input skill.

---

## Active Backlog

### High Priority

| ID | Item | Status | Owner | Target |
|----|------|--------|-------|--------|
| **VI-001** | Add real human voice fixture for accuracy testing | TODO | @carlosfrias | v1.1.0 |
| **VI-002** | Implement command confirmation dialog before execution | TODO | — | v1.1.0 |
| **VI-003** | Add voice command audit log rotation (30-day retention) | TODO | — | v1.2.0 |

### Medium Priority

| ID | Item | Status | Owner | Target |
|----|------|--------|-------|--------|
| **VI-010** | Support for custom wake word ("Hey Trading Desk") | Research | — | v1.3.0 |
| **VI-011** | Multi-language support (Spanish, Mandarin) | Backlog | — | v2.0.0 |
| **VI-012** | Voice response feedback (TTS confirmation) | Backlog | — | v1.4.0 |

### Low Priority

| ID | Item | Status | Owner | Target |
|----|------|--------|-------|--------|
| **VI-020** | Integration with voice biometrics for auth | Idea | — | Future |
| **VI-021** | Custom model fine-tuning on trading jargon | Backlog | — | v2.1.0 |

---

## Bugs

| ID | Description | Severity | Status |
|----|-------------|----------|--------|
| **VIB-001** | Transcription latency >2s on low-end hardware | Medium | Investigating |
| **VIB-002** | False positives on keyboard typing noise | Low | Confirmed |

---

## Completed

| ID | Item | Completed | PR |
|----|------|-----------|-----|
| **VI-100** | Initial Voxtype integration | 2026-05-10 | #1 |
| **VI-101** | Acceptance test suite (7 suites) | 2026-05-10 | #2 |
| **VI-102** | CI/CD pipeline with self-hosted runner | 2026-05-10 | #3 |
| **VI-103** | Security test suite (injection prevention) | 2026-05-10 | #4 |
| **VI-104** | Wiki documentation published | 2026-05-10 | #5 |

---

## Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Transcription accuracy | ≥80% (synthetic) | ≥95% (real voice) |
| End-to-end latency | <3s | <1s |
| False positive rate | <5% | <1% |
| Test coverage | 7 suites | 10 suites |

---

## Notes

- **Repository**: https://github.com/carlosfrias/voice-input-acceptance-tests (private)
- **Test runner**: `technical-infrastructure/packages/voice-input/acceptance-tests/scripts/run-all.sh`
- **Documentation**: [`/technical-infrastructure/wiki/guides/voice-input-guide.md`](../guides/voice-input-guide.md)

---

## How to Contribute

1. Pick an item from the backlog
2. Create a branch: `git checkout -b feature/VI-XXX`
3. Implement + write tests
4. Run acceptance suite: `./scripts/run-all.sh`
5. Submit PR with test results

---

**Last updated:** 2026-05-10  
**Maintainer:** @carlosfrias
