# Dictation: Local Speech-to-Text with Whisper.cpp + Hammerspoon
**Installed:** 2026-05-01  
**Last Updated:** 2026-05-01  
**Location:** macOS Orchestrator (this node)

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/dictation-setup.md`

---

## What This Is

Local speech-to-text that runs entirely on your Mac — no cloud, no internet, no subscription. You press a hotkey, speak, and the transcribed text lands on your clipboard. Then you paste it wherever you need.

## Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Whisper.cpp** | Speech-to-text engine (OpenAI Whisper rewritten in C++) | `~/whisper.cpp/` |
| **whisper-cli** | The actual transcription binary | `~/whisper.cpp/build/bin/whisper-cli` |
| **ggml-base.en.bin** | English speech model (141MB) | `~/whisper.cpp/models/` |
| **ffmpeg** | Records 5 seconds from your Mac's microphone | `/usr/local/bin/ffmpeg` |
| **Hammerspoon** | macOS automation framework — intercepts hotkey, runs script | `/Applications/Hammerspoon.app` |
| **dictate.sh** | Your wrapper — ties it all together | `~/bin/dictate.sh` |

## How It Works (The Full Flow)

### Press → Speak → Wait → Paste

```
You press Cmd+Shift+D → [Hotkey captured by Hammerspoon]
                          ↓
                    ffmpeg records 5 sec of audio
                          ↓
                    Temporary WAV file created
                          ↓
                    whisper-cli transcribes it
                          ↓
                    Text copied to clipboard (pbcopy)
                          ↓
                    Popup shows: "Dictated: your text here"
                    ☝️ The text is on your clipboard NOW
                          ↓
                    ┌─────────────────────────────┐
                    │  KEY STEP: Cmd+V to paste   │
                    │  wherever your cursor is    │
                    └─────────────────────────────┘
```

## Important: The Paste Step

**The dictation output does NOT type into your window automatically.** It goes to the clipboard. You must press `Cmd+V` to paste it.

**Flow:**
1. Press hotkey → wait for popup
2. Place cursor where you want text
3. Press `Cmd+V` to paste

**Tip:** The popup is just confirmation. You can paste as soon as you hear the audio recording stop (about 5 seconds after pressing the hotkey) — you don't have to wait for the popup.

## Hotkey

| Default | Action |
|---------|--------|
| `Cmd+Shift+D` | Trigger dictation |
| `Cmd+V` | Paste the transcribed text |

### ⚠️ Browser Conflict

`Cmd+Shift+D` is also the default for **Safari** (Add to Reading List) and **Chrome** (Bookmark all tabs). Hammerspoon intercepts it first, so browsers never see the key — but other apps on your Mac won't either.

**To resolve:** Change the hotkey. See [Hotkey Customization](#hotkey-customization) below.

## Model Info

| Model | Size | Quality | Speed | Best For |
|-------|------|---------|-------|----------|
| **base.en** (current) | 141MB | Good | ~0.7s/10s audio | General dictation, speed over precision |
| small.en | 466MB | Better | ~1.5s/10s audio | More accuracy, still fast |
| medium.en | 1.5GB | Excellent | ~4s/10s audio | Complex vocabulary, formal writing |

Current model is `base.en` — optimized for fast, everyday dictation on Apple Silicon.

## How to Dictate

1. **Position your cursor** where you want the text (a text field, document, terminal, etc.)
2. **Speak clearly** toward your Mac's microphone
3. **Wait** for the recording to finish (5 seconds fixed, or release when done)
4. **Click or ensure window focus** is where you want the text
5. **Press `Cmd+V`** to paste
6. **Edit** the text (Whisper sometimes adds trailing spaces or mishears proper nouns)

**Example:**
- You: *press Cmd+Shift+D* → "send email to Alice about the budget meeting on Tuesday"
- Popup: "Dictated: send email to Alice about the budget meeting..."
- You: `Cmd+V` → text appears in your email

## Hotkey Customization

Edit `~/.hammerspoon/init.lua`:

```lua
-- Current:
hs.hotkey.bind({"cmd", "shift"}, "D", function()

-- Change to any of these:
 hs.hotkey.bind({"cmd", "ctrl"}, "D", function())      -- Cmd+Ctrl+D
 hs.hotkey.bind({"cmd", "alt"}, "D", function())       -- Cmd+Option+D
 hs.hotkey.bind({"ctrl", "alt"}, "D", function())      -- Ctrl+Option+D
 hs.hotkey.bind({"cmd", "shift"}, "R", function())     -- Cmd+Shift+R
 hs.hotkey.bind({}, "F6", function())                   -- Just F6
```

**After editing:** Click the Hammerspoon menu bar spoon icon → **Reload Config**

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Nothing happens | Hammerspoon not running | Start it from Applications |
| Popup says "no speech detected" | Microphone too quiet or muted | Check mic permissions (System Settings → Privacy → Microphone) |
| Popup shows wrong/ garbled text | Whisper misheard | Speak more clearly, or upgrade to `small.en` model |
| Safari/Chrome bookmark dialog appears | You're in browser, Hammerspoon didn't capture | Check Hammerspoon is running. Or change hotkey. |
| "Dictation failed" popup | ffmpeg missing or mic blocked | `which ffmpeg` — if missing, `brew install ffmpeg`. Check mic permissions. |
| Text pastes but then disappears | Focus changed before paste | Wait for popup, then click where you want text, then Cmd+V |

## Files

| File | What It Is |
|------|-----------|
| `~/.hammerspoon/init.lua` | Hammerspoon configuration (hotkey definition) |
| `~/bin/dictate.sh` | Dictation wrapper script (ffmpeg + whisper + clipboard) |
| `~/whisper.cpp/compile.sh` | Build script (already ran) |
| `~/whisper.cpp/models/ggml-base.en.bin` | English speech model |

## Model Upgrades

To use a more accurate model:

```bash
cd ~/whisper.cpp
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin" -o models/ggml-small.en.bin

# Edit ~/bin/dictate.sh, change this line:
# MODEL="$WHISPER_DIR/models/ggml-base.en.bin"
# To:
# MODEL="$WHISPER_DIR/models/ggml-small.en.bin"
```

## Core ML Acceleration (Apple Silicon Speedup)

For 2-3x faster transcription on M1/M2/M3 Macs:

```bash
cd ~/whisper.cpp
./models/download-coreml-model.sh base.en
python3 convert-whisper-to-coreml.py --model base.en
# Then use whisper-cli with -coreml flag in dictate.sh
```

Note: Core ML support is ongoing in whisper.cpp — check compatibility before enabling.

## Related

- [Whisper.cpp GitHub](https://github.com/ggerganov/whisper.cpp)
- [Hammerspoon Documentation](https://www.hammerspoon.org/docs/)
- Model source: [HuggingFace ggerganov/whisper.cpp](https://huggingface.co/ggerganov/whisper.cpp)
