# BOOKMARK — STT Pipeline: Decomposed Spikes

**Bookmarked:** 2026-05-17  
**Status:** Ready to execute, blocked on session target  
**Resume trigger:** "continue STT spikes" or "follow up on bookmark"

---

## What's Bookmarked

Full decomposition of the STT plan's 6 "Next Steps" from `workshop/01-Projects/kingdom-warfare-leadership/data/stt-plan.md`.

## Decomposed Sub-Tasks (for 4B model execution)

### Chain 1: Video URL Extraction
| # | Task | Status |
|---|------|--------|
| 1.1 | Read curriculum JSON, print first lesson URL | ⏳ |
| 1.2 | Write `scripts/spike-video-src.py` (Playwright → video.src) | ⏳ |
| 1.3 | Run spike script, report video source | ⏳ |
| 1.4 | Enhance with `page.route()` network interception | ⏳ |

### Chain 2: mlx-whisper Install + Test
| # | Task | Status |
|---|------|--------|
| 2.1 | `pip install mlx-whisper`, confirm version | ⏳ |
| 2.2 | Create 30s test audio, transcribe, report timing | ⏳ |

### Chain 3: Post-Processing Scripts
| # | Task | Status |
|---|------|--------|
| 3.1 | Write `scripts/process-transcript.py` (clean + format) | ⏳ |
| 3.2 | Write `scripts/detect-scripture.py` (Bible ref patterns) | ⏳ |

## Unresolved

- **No `spike-1` intercom session** — need to decide: use existing `subagent-chat-019e38d4` (gemma4:e4b), create new session, or spawn agent.
- **`psutil` not installed** — health monitor can't do RAM/CPU checks (low priority for docs task).

## Key Files

- STT Plan: `workshop/01-Projects/kingdom-warfare-leadership/data/stt-plan.md`
- Curriculum extract: `workshop/01-Projects/kingdom-warfare-leadership/data/curriculum-extract-2026-05-17.json`
- Decomposition skill: `/Users/friasc/.pi/agent/skills/decompose-execute-verify/SKILL.md`

## Resume

Chains 1, 2, and 3 are independent. When resumed, pick a session target and start with Chain 1 (highest risk, determines capture approach).
