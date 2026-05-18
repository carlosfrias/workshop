# Voxtype Reference

Push-to-talk voice-to-text tool for Linux and macOS desktop environments.

---

## Overview

**Voxtype** is a desktop-native speech-to-text utility optimized for Wayland and X11. It uses Whisper.cpp under the hood for offline transcription.

**Homepage:** https://voxtype.io  
**Source:** https://github.com/peteonrails/voxtype

---

## Installation

### Build from Source

```bash
# Dependencies (Arch)
sudo pacman -S --needed base-devel rust clang alsa-lib wtype wl-clipboard

# Clone and build
git clone https://github.com/peteonrails/voxtype /opt/voxtype
cd /opt/voxtype
cargo build --release

# Verify
/opt/voxtype/target/release/voxtype --version
```

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4 GB | 8 GB (for large models) |
| **CPU** | 2 cores | 4+ cores |
| **GPU** | Optional | NVIDIA CUDA for acceleration |
| **Disk** | 2 GB | 10 GB (multiple models) |

---

## CLI Reference

### Basic Usage

```bash
# Push-to-talk mode (hold SCROLLLOCK to record)
voxtype --push-to-talk

# Record for fixed duration
voxtype --record --duration 5 --output /tmp/output.wav

# Transcribe existing audio file
voxtype --input /tmp/audio.wav --output -

# Pipe audio from stdin
cat audio.wav | voxtype --stdin --output -

# Copy transcription to clipboard
voxtype --push-to-talk --clipboard
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--push-to-talk` | Enable push-to-talk mode | `false` |
| `--record` | Record audio (requires duration or manual stop) | `false` |
| `--duration <sec>` | Recording duration in seconds | `none` |
| `--input <file>` | Input audio file path | `stdin` |
| `--output <file>` | Output file (use `-` for stdout) | `stdout` |
| `--stdin` | Read audio from stdin | `false` |
| `--clipboard` | Copy output to clipboard | `false` |
| `--model <name>` | Whisper model to use | `large-v3-turbo` |
| `--device <name>` | Audio input device | `default` |
| `--threshold <float>` | Audio level threshold (0.0-1.0) | `0.02` |
| `--silence-timeout <sec>` | Stop after silence duration | `10` |

### Models

```bash
# List available models
voxtype --help | grep -A 20 "model"

# Use specific model
voxtype --model tiny --push-to-talk        # Fast, low accuracy
voxtype --model large-v3-turbo --push-to-talk  # Slow, high accuracy
```

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny` | 39 MB | ⚡⚡⚡ | ⭐ | Quick commands |
| `base` | 74 MB | ⚡⚡ | ⭐⭐ | General use |
| `small` | 244 MB | ⚡ | ⭐⭐⭐ | Balanced |
| `medium` | 769 MB | 🐌 | ⭐⭐⭐⭐ | Financial terms |
| `large-v3` | 3.1 GB | 🐌 | ⭐⭐⭐⭐⭐ | Maximum accuracy |
| `large-v3-turbo` | 3.1 GB | 🐌 | ⭐⭐⭐⭐⭐ | **Recommended** |

---

## Configuration

### Config File Location

```bash
# Linux
~/.config/voxtype/config.toml

# macOS
~/Library/Application Support/voxtype/config.toml
```

### Example Configuration

```toml
# ~/.config/voxtype/config.toml

[hotkey]
# Main push-to-talk key (Linux evdev key name)
push_to_talk = "SCROLLLOCK"
# Alternative: use compositor keybinding
use_compositor_binding = true

[models]
# Default model for transcription
default = "large-v3-turbo"
# Model download directory
cache_dir = "~/.cache/voxtype/models"

[recording]
# Audio format
sample_rate = 16000
channels = 1
bit_depth = 16
# Silence detection
threshold = 0.02
silence_timeout = 10

[output]
# Output format: text, json, srt, vtt
format = "text"
# Auto-copy to clipboard
auto_clipboard = false
# Output file pattern
output_pattern = "~/recordings/voxtype-%Y%m%d-%H%M%S.txt"

[advanced]
# GPU acceleration (NVIDIA CUDA)
use_cuda = false
# CPU threads
threads = 4
# Batch size for processing
batch_size = 16
# Debug logging
log_level = "info"
```

---

## Integration Examples

### Pipe to pi Agent

```bash
# Direct pipeline
voxtype --push-to-talk --output - | ~/bin/pi --cli

# With logging
voxtype --push-to-talk --output - | tee ~/.pi/voice-commands.log | ~/bin/pi --cli
```

### Shell Function

Add to `~/.bashrc`:

```bash
voxpi() {
  local transcript
  transcript=$(voxtype --push-to-talk --output - 2>/dev/null)
  echo "🎤 Voice command: $transcript"
  echo "$transcript" | ~/bin/pi --cli
}
```

### systemd Service

```ini
# /etc/systemd/system/voxtype.service
[Unit]
Description=Voxtype Voice Input Daemon
After=basic.target

[Service]
Type=simple
ExecStart=/opt/voxtype/target/release/voxtype --push-to-talk --model large-v3-turbo
Restart=on-failure
User=trading-user
Environment=VOXTYPE_CONFIG=/home/trading-user/.config/voxtype/config.toml

[Install]
WantedBy=default.target
```

---

## Troubleshooting

### Audio Not Detected

```bash
# List audio devices
arecord -l

# Test recording
arecord -d 2 -f cd /tmp/test.wav && aplay /tmp/test.wav

# Check PulseAudio/PipeWire
pactl list sources short
```

### Model Download Issues

```bash
# Manually download model
cd ~/.cache/voxtype/models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin

# Verify checksum
sha256sum ggml-large-v3-turbo.bin
```

### Permission Errors

```bash
# Add user to audio group
sudo usermod -aG audio $USER

# Check device permissions
ls -la /dev/snd/
```

### Performance Issues

```toml
# ~/.config/voxtype/config.toml
[advanced]
# Reduce threads for lower CPU usage
threads = 2
# Use smaller model
default = "small"
```

---

## Testing

### Quick Tests

```bash
# Version check
voxtype --version

# Help output
voxtype --help

# Record and playback
voxtype --record --duration 3 --output /tmp/test.wav
aplay /tmp/test.wav

# Transcribe fixture
echo "test" | voxtype --stdin --output -
```

### Acceptance Tests

See [`../guides/voice-input-guide.md`](../guides/voice-input-guide.md#testing) for full test suite.

---

## Security Notes

- **Offline by default**: No audio leaves your machine
- **No telemetry**: Voxtype does not phone home
- **Local models**: All ML models stored locally in `~/.cache/voxtype/`
- **Audit trail**: Log all voice commands to `~/.pi/voice-commands.log`

---

## Related

- [Voice Input Guide](../guides/voice-input-guide.md)
- [Acceptance Tests](https://github.com/carlosfrias/voice-input-acceptance-tests)
- [Whisper.cpp Documentation](https://github.com/ggerganov/whisper.cpp)
