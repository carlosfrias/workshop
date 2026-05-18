# Speech-to-Text Pipeline Plan — Kingdom Warfare Course Videos

**Status:** PLAN (do not execute)  
**Date:** 2026-05-17  
**Context:** Kingdom Warfare courses are video-only (no transcripts). Need to transcribe 5 courses × 61 lessons into text for study aids.

---

## [S-TIGHT]

Three-phase pipeline: Capture audio → Transcribe with local Whisper → Post-process into structured markdown. Recommended: network interception for video download (avoids real-time playback), mlx-whisper with large-v3-turbo model for transcription (2x faster than whisper.cpp on Apple Silicon).

---

## Current State

| Item | Status |
|------|--------|
| Course structure extracted | ✅ `data/curriculum-extract-2026-05-17.json` — 17 courses, 200+ lessons mapped |
| Browser auth working | ✅ Playwright with `CLIENTCLUB_EMAIL`/`CLIENTCLUB_PASSWORD` from `~/.local/bin/env` |
| Video player identified | ✅ Plyr (plyr.io), blob: URLs, no subtitle tracks in DOM |
| `ffmpeg` | ✅ `/usr/local/bin/ffmpeg` |
| BlackHole audio loopback | ❌ Not installed |
| `mlx_whisper` | ❌ Not installed (`pip install mlx-whisper`) |

---

## Phase 1: Audio Acquisition

### Approach A: Network Interception + Download ⭐ RECOMMENDED

**How it works:** Use Playwright's `page.route()` to intercept network requests, capture the actual video file URL (behind the blob), download it directly, and extract audio with ffmpeg. No real-time playback needed.

**Why this wins:**
- Downloads at network speed, not 1× playback speed
- No audio quality loss from re-recording
- No dependency on BlackHole or system audio routing
- Can run headless, fully unattended

**Implementation sketch:**

```python
# playwright_capture.py
import asyncio
from playwright.async_api import async_playwright
import os

async def capture_video_url(course_url):
    video_urls = []
    
    async def handle_route(route):
        url = route.request.url
        # Video files typically end in .mp4, .m3u8, .ts, or come from streaming endpoints
        if any(ext in url for ext in ['.mp4', '.m3u8', 'video', 'media', 'stream']):
            video_urls.append(url)
        await route.continue_()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Intercept all network requests
        await page.route("**/*", handle_route)
        
        # Navigate and authenticate
        await page.goto(course_url)
        # ... login flow ...
        
        # Navigate to lesson, wait for video player
        await page.wait_for_selector('video, .plyr, [data-plyr]')
        await page.wait_for_timeout(5000)  # Let video source load
        
        # Try to extract video source from DOM
        src = await page.evaluate("""() => {
            const v = document.querySelector('video');
            return v ? (v.currentSrc || v.src) : null;
        }""")
        
        await browser.close()
        return video_urls, src
```

**Alternative — blob download from within the page:**

If the video source is only accessible as a blob URL, download it via in-page fetch:

```python
# Fetch blob and return as base64
video_data = await page.evaluate("""async () => {
    const video = document.querySelector('video');
    const blobUrl = video.src || video.currentSrc;
    const response = await fetch(blobUrl);
    const blob = await response.blob();
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.readAsDataURL(blob);
    });
}""")
```

### Approach B: BlackHole + System Audio Recording FALLBACK

**Use if:** Network interception fails (DRM, encrypted streams, complex auth on video URLs).

**Setup (one-time):**
1. Install BlackHole: `brew install blackhole-2ch`
2. Open **Audio MIDI Setup** → create Multi-Output Device:
   - Check: "BlackHole 2ch" + your speakers/headphones
3. Set as system output before recording

**Recording flow:**
1. Set macOS audio output → Multi-Output Device
2. Start audio recording: `sox -t coreaudio "BlackHole 2ch" lesson-01.wav &`
3. Play video via Playwright (automated navigation + click play)
4. Wait for video duration, then stop sox
5. Reset audio output to normal

**Command:**
```bash
# Install deps
brew install blackhole-2ch sox

# Record system audio (run in background)
sox -t coreaudio "BlackHole 2ch" output.wav &
SOX_PID=$!

# ... Play video via Playwright ...

kill $SOX_PID
```

**Tradeoffs:**
- ⚠️ Requires real-time playback (61 lessons × ~10 min = ~10 hours of wall-clock time just for recording)
- ⚠️ Audio quality limited by system audio pipeline
- ⚠️ Machine can't be used for other audio during recording
- ✅ Works with any audio source, regardless of DRM

### Approach C: Web Audio API Capture EXPERIMENTAL

Capture audio from within the browser using the Web Audio API:

```javascript
// Inject into page
const stream = document.querySelector('video').captureStream();
const audioCtx = new AudioContext();
const source = audioCtx.createMediaStreamSource(stream);
const dest = audioCtx.createMediaStreamDestination();
source.connect(dest);

const recorder = new MediaRecorder(dest.stream);
const chunks = [];
recorder.ondataavailable = e => chunks.push(e.data);
recorder.onstop = () => {
    const blob = new Blob(chunks, {type: 'audio/webm'});
    // Send blob to Python side
};
recorder.start();
```

**Tradeoffs:**
- ⚠️ Playwright headless Chromium uses `--mute-audio` (must launch headed)
- ⚠️ `captureStream()` may not work on cross-origin media elements
- ⚠️ MediaRecorder only outputs lossy formats (webm/opus)
- ❌ Not recommended as primary approach

---

## Phase 2: Transcription

### Tool Selection: mlx-whisper

| Criterion | mlx-whisper | whisper.cpp |
|-----------|-------------|-------------|
| **Speed (Apple Silicon)** | **13s for 12min audio** (55× real-time) | 27s for 12min audio (27× real-time) |
| **Relative performance** | **2.0× faster** | baseline |
| **GPU acceleration** | MLX (Apple Silicon native) | CoreML (via GGML) |
| **Model sizes** | tiny (39M) → large-v3-turbo (809M) | same range |
| **Install** | `pip install mlx-whisper` | `git clone + make` |
| **Output formats** | txt, vtt, srt, tsv, json | txt, vtt, srt, json |
| **Python API** | `mlx_whisper.transcribe()` | subprocess wrapper needed |

**Recommendation:** `mlx-whisper` with `mlx-community/whisper-large-v3-turbo` model.

### Model Selection

| Model | Parameters | Speed | Accuracy | Use Case |
|-------|-----------|-------|----------|----------|
| `whisper-tiny` | 39M | fastest | lowest | Testing, quick drafts |
| `whisper-small` | 244M | fast | moderate | — |
| `whisper-medium` | 769M | moderate | good | Budget option |
| `whisper-large-v3-turbo` | 809M | fast | **excellent** | ⭐ Best quality/speed tradeoff |
| `whisper-large-v3` | 1.5B | slowest | best | Maximum accuracy |

**Recommendation:** `whisper-large-v3-turbo` — nearly large-v3 accuracy at ~8× faster speed.

### Installation

```bash
pip install mlx-whisper
```

First run auto-downloads the model from Hugging Face Hub (~1.5GB).

### Transcription Command

```bash
# Single file
mlx_whisper lesson-01.wav \
  --model mlx-community/whisper-large-v3-turbo \
  --output-format all \
  --output-dir ./transcripts/lesson-01/

# Batch processing
for f in audio/*.wav; do
  lesson=$(basename "$f" .wav)
  mlx_whisper "$f" \
    --model mlx-community/whisper-large-v3-turbo \
    --output-format all \
    --output-dir "./transcripts/$lesson/"
done
```

### Python API (for programmatic use)

```python
import mlx_whisper

result = mlx_whisper.transcribe(
    "lesson-01.wav",
    path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
    word_timestamps=True,
)

print(result["text"])           # Full text
for seg in result["segments"]:  # Per-segment with timestamps
    print(f"[{seg['start']:.1f}s] {seg['text']}")
```

### Output: JSON Segment Structure

```json
{
  "text": "Full transcription text...",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 4.5,
      "text": " Welcome to Kingdom Warfare.",
      "words": [
        {"word": "Welcome", "start": 0.0, "end": 0.7},
        {"word": "to", "start": 0.7, "end": 0.9},
        ...
      ]
    }
  ],
  "language": "en"
}
```

---

## Phase 3: Post-Processing → Structured Markdown

### Step 1: Clean Transcription

Python script to:
- Remove filler words (um, uh, you know)
- Fix capitalization (start of sentences)
- Normalize punctuation
- Merge short segments for readability

### Step 2: Identify Bible References

Course content is Scripture-heavy. Detect patterns:
- "Book Chapter:Verse" (e.g., "Ephesians 6:12")
- "Book chapter verse" (e.g., "Matthew five twelve")
- Spoken abbreviations ("First Peter two twenty-four")

Convert to consistent format: `[[Scripture/Ephesians#6:12|Ephesians 6:12]]`

### Step 3: Structure as Markdown

Output format for each lesson:

```markdown
# Course 01 — Lesson 03: The Armor of God

**Duration:** 12:34  
**Transcribed:** 2026-05-17  
**Source:** [Course link]

## Summary

Brief AI-generated summary of the lesson.

## Transcript

[00:00] Welcome to this lesson on the Armor of God...

[02:15] Paul writes in Ephesians chapter 6...

## Key Scriptures

- [[Scripture/Ephesians#6:12|Ephesians 6:12]] — "For we wrestle not against flesh and blood..."
- [[Scripture/Ephesians#6:14|Ephesians 6:14]] — "Stand therefore, having your loins girt about with truth..."

## Key Concepts

- **Spiritual warfare** — Not physical but spiritual battle
- **Armor of God** — Each piece represents a spiritual discipline

## Discussion Questions

1. What does it mean to "wrestle not against flesh and blood"?
2. How do you practically "put on the full armor of God" daily?
```

### Step 4: Batch Generation

One script that processes all 61 lessons:

```
transcribe-all.sh
├── 1. For each course/lesson
│   ├── Download audio (or extract from video)
│   ├── Transcribe with mlx-whisper
│   └── Post-process → markdown
├── 2. Generate course index
└── 3. Generate flashcard decks from extracted concepts
```

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────┐
│                   INPUT                              │
│  curriculum-extract-2026-05-17.json                  │
│  (course URLs, lesson URLs, titles)                  │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              PHASE 1: AUDIO CAPTURE                  │
│                                                      │
│  ┌──────────────────────┐  ┌────────────────────┐   │
│  │ Network Interception │  │ BlackHole + Sox    │   │
│  │ (preferred)          │  │ (fallback)         │   │
│  │                      │  │                    │   │
│  │ page.route() → URLs  │  │ System audio → WAV │   │
│  │ → download → ffmpeg  │  │                    │   │
│  └──────────┬───────────┘  └─────────┬──────────┘   │
│             │                        │               │
│             └────────┬───────────────┘               │
│                      ▼                               │
│              .wav audio files                        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│           PHASE 2: TRANSCRIPTION                     │
│                                                      │
│  mlx-whisper                                         │
│  --model mlx-community/whisper-large-v3-turbo       │
│  --output-format all                                 │
│                                                      │
│  Speed: ~55× real-time (13s per 12min audio)         │
│  Output: JSON with segments, VTT, TXT, SRT           │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│         PHASE 3: POST-PROCESSING                     │
│                                                      │
│  ┌────────────┐  ┌───────────┐  ┌──────────────┐   │
│  │ Clean text │→│ Scripture  │→│ Markdown      │   │
│  │ (filler,   │  │ detection │  │ formatting    │   │
│  │  punct.)   │  │ + linking │  │ + structure   │   │
│  └────────────┘  └───────────┘  └──────────────┘   │
│                                                      │
│  Output: personal-vault/01-Projects/                 │
│          kingdom-warfare-leadership/curriculum/      │
└─────────────────────────────────────────────────────┘
```

---

## Time & Resource Estimates

### Per-Video Breakdown (avg. 10 min video)

| Step | Tool | Time |
|------|------|------|
| Download video / extract audio | Playwright + ffmpeg | ~30s |
| Audio extraction (if video downloaded) | ffmpeg | ~10s |
| Transcription | mlx-whisper (large-v3-turbo) | ~15s |
| Post-processing | Python script | ~30s |
| **Total per lesson** | | **~1.5 min** |

### Per-Course Breakdown

| Course | Lessons | Est. Time |
|--------|---------|-----------|
| Course 01 | ~12 | ~18 min |
| Course 02 | ~12 | ~18 min |
| Course 03 | ~12 | ~18 min |
| Course 04 | ~12 | ~18 min |
| Course 05 | ~13 | ~20 min |
| **Total** | **~61 lessons** | **~1.5 hours** |

### Disk Usage

| Item | Size |
|------|------|
| Downloaded videos (per lesson) | ~50-150 MB |
| Extracted audio (per lesson) | ~10-20 MB |
| Transcription outputs (per lesson) | ~50 KB |
| Model download (one-time) | ~1.5 GB |
| **Total for all 61 lessons** | **~5-10 GB** (temporary; videos deletable after extraction) |

---

## Dependencies to Install

```bash
# STT engine
pip install mlx-whisper

# Audio loopback (only needed for Approach B — fallback)
brew install blackhole-2ch sox

# Already available:
# - ffmpeg: /usr/local/bin/ffmpeg ✅
# - Playwright: for browser automation ✅
```

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Video URLs use DRM / encrypted HLS | Medium | Fall back to BlackHole real-time recording (Approach B) |
| Server requires short-lived tokens on video URLs | High | Intercept auth headers, include in download requests |
| Blob URLs can't be fetched from outside page context | Medium | Download blob via in-page `fetch()` → base64 → Python |
| Whisper hallucinates Scripture references | Low | Use `--hallucination_silence_threshold` and post-process validation |
| Course content exceeds model context window | None | Whisper processes in 30s chunks natively |
| Speaker has strong accent / multiple speakers | Low | large-v3-turbo handles this well; no diarization needed |

---

## Next Steps (after plan approval)

1. **Spike: Video URL extraction** — Write a small Playwright script that navigates to one lesson and logs all network requests. Confirm we can capture the actual video URL.
2. **Spike: Blob download** — If blob URLs only, test in-page fetch approach.
3. **Install mlx-whisper** — `pip install mlx-whisper`, test on a short sample.
4. **Build capture script** — Full automation: auth → navigate → capture → extract audio.
5. **Build transcription script** — Batch process all .wav files.
6. **Build post-processing** — Clean → detect references → format markdown.

---

*Plan version: 1.0 — Research complete, ready for review.*
