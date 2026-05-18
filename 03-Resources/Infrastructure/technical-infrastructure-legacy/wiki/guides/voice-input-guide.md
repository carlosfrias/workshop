# Voice Input Guide

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/voice-input-guide.md`

Hands-free voice command execution for the Trading Desk via [Voxtype](https://voxtype.io) push-to-talk transcription.

---

## Overview

Voice input enables traders to execute commands without typing:

```
Microphone → Voxtype (Whisper ASR) → Text → pi agent stdin → Command Execution
```

**Use cases:**
- Quick position checks while monitoring screens
- Hands-free trade logging during active sessions
- Rapid research queries without context switching
- Accessibility for traders with mobility constraints

**Security model:** Voice input is **non-audited input**. All voice commands are logged and should be reviewed periodically.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **OS** | Linux (Wayland or X11) or macOS |
| **Audio** | Working microphone (`arecord -l` shows devices) |
| **Build tools** | `base-devel`, `rust`, `cargo` |
| **pi agent** | Installed at `~/bin/pi` or in `$PATH` |
| **Network** | Access to GitHub for Voxtype source |

---

## Installation

### Step 1: Install System Dependencies

```bash
# Arch/Manjaro
sudo pacman -S --needed base-devel rust clang alsa-lib wtype wl-clipboard sox

# Ubuntu/Debian
sudo apt-get install -y build-essential rustc cargo libasound2-dev \
  libwayland-dev libxkbcommon-dev libpulse-dev sox

# macOS (Homebrew)
brew install rust cargo sox
```

### Step 2: Build Voxtype

```bash
# Clone the repository
git clone https://github.com/peteonrails/voxtype /opt/voxtype
cd /opt/voxtype

# Build release binary
cargo build --release

# Verify installation
/opt/voxtype/target/release/voxtype --version
# Expected: "voxtype 1.x.x"
```

### Step 3: Add to PATH (Optional)

```bash
# Create symlink
sudo ln -s /opt/voxtype/target/release/voxtype /usr/local/bin/voxtype

# Verify
which voxtype
voxtype --help
```

### Step 4: Configure Audio Permissions

```bash
# Linux: Add user to audio group
sudo usermod -aG audio $USER

# Verify microphone access
arecord -l
arecord -d 2 -f cd /tmp/test-mic.wav && aplay /tmp/test-mic.wav
```

---

## Configuration

### Voxtype Settings

Create or edit `~/.config/voxtype/config.toml`:

```toml
# ~/.config/voxtype/config.toml

[hotkey]
# Hold SCROLLLOCK to record, release to stop
push_to_talk = "SCROLLLOCK"

[models]
# Best accuracy for financial terminology
default = "large-v3-turbo"

[output]
# Output format: text, json, or clipboard
format = "text"

[advanced]
# Timeout after 10s of silence
silence_timeout = 10
# Minimum audio level to trigger recording
threshold = 0.02
```

### Model Selection

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| `tiny` | ⚡⚡⚡ | ⭐ | Quick commands, low latency |
| `base` | ⚡⚡ | ⭐⭐ | General use |
| `small` | ⚡ | ⭐⭐⭐ | Balanced |
| `medium` | 🐌 | ⭐⭐⭐⭐ | Financial terminology |
| `large-v3-turbo` | 🐌 | ⭐⭐⭐⭐⭐ | **Recommended** for trading desk |

---

## Usage

### Basic Push-to-Talk

```bash
# Start Voxtype (hold SCROLLLOCK to speak)
voxtype --push-to-talk

# Speak your command, release SCROLLLOCK to stop
# Output appears to stdout
```

### Direct Pipe to pi Agent

```bash
# Method 1: One-liner (hold SCROLLLOCK, speak, release)
voxtype --push-to-talk --output - | ~/bin/pi --cli

# Method 2: Two-step (record first, then pipe)
voxtype --record --output /tmp/voice-command.txt
# ... speak when prompted ...
cat /tmp/voice-command.txt | ~/bin/pi --cli
```

### Create a Shell Alias

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Voice command shortcut
alias voxpi='voxtype --push-to-talk --output - | ~/bin/pi --cli'

# Usage: voxpi
# Hold SCROLLLOCK, speak "Show BTC positions", release
```

### Example Commands

```bash
# Position check
"Trading desk, show open positions for BTC and ETH"

# Trade logging
"Log buy 0.5 BTC at 68000 USD, timestamp now"

# Market research
"Analyze volatility skew for SPY options expiring this Friday"

# Risk monitoring
"Check portfolio delta exposure and margin utilization"
```

---

## Testing

### Run Acceptance Tests

The voice-input skill includes a comprehensive test suite:

```bash
cd technical-infrastructure/packages/voice-input/acceptance-tests

# Generate test fixtures (synthetic audio)
./scripts/generate-fixtures.sh

# Run all tests
./scripts/run-all.sh --verbose

# Run a specific suite
./scripts/run-all.sh --suite smoke      # Binary presence
./scripts/run-all.sh --suite hardware   # Audio device detection
./scripts/run-all.sh --suite recording  # Transcription accuracy
./scripts/run-all.sh --suite security   # Injection prevention
./scripts/run-all.sh --suite integration # End-to-end pipeline

# Generate JUnit XML report (for CI)
./scripts/run-all.sh --junit report.xml
```

### Test Suites

| Suite | Tests | Pass Criteria |
|-------|-------|---------------|
| `smoke` | Binary exists, help works | Exit code 0 |
| `hardware` | Mic detected, ALSA works | ≥1 device found |
| `recording` | Reference phrase transcription | ≥80% word accuracy |
| `model` | Config parses, models available | Valid TOML, known models |
| `integration` | Voice→text→pi pipeline | Non-empty pi response |
| `edge-cases` | Silence, noise, long input | No crashes, graceful handling |
| `security` | Injection attempts blocked | Payloads treated as literal text |

### Manual Testing

```bash
# Test 1: Verify Voxtype responds
voxtype --version

# Test 2: Record 3 seconds of audio
voxtype --record --duration 3 --output /tmp/test.wav

# Test 3: Transcribe a fixture
cat fixtures/reference-phrase.wav | voxtype --stdin --output -

# Test 4: Pipe to pi agent
echo "Test voice command" | ~/bin/pi --cli
```

---

## CI/CD Integration

### GitHub Actions Workflow

The acceptance tests run on a **self-hosted runner** with microphone hardware:

```yaml
# .github/workflows/acceptance.yml
jobs:
  acceptance:
    runs-on: [self-hosted, linux, microphone]
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/run-all.sh --junit report.xml
```

### Set Up Self-Hosted Runner

```bash
# On a machine with microphone hardware:
cd ~/actions-runner
./config.sh --url https://github.com/carlosfrias/voice-input-acceptance-tests \
  --token <TOKEN> --labels linux,microphone

# Start the runner
./run.sh
```

### Pre-Push Hook

Install the pre-push hook to run tests before every push:

```bash
cd technical-infrastructure/packages/voice-input/acceptance-tests
cp .githooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

---

## Troubleshooting

### Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| `voxtype: command not found` | Not in PATH | `sudo ln -s /opt/voxtype/target/release/voxtype /usr/local/bin/voxtype` |
| `arecord: device not found` | No mic detected | Check `alsamixer`, ensure not muted |
| Transcription is empty | Model not downloaded | Run `voxtype --model large-v3-turbo` once to trigger download |
| pi agent doesn't respond | stdin not piped | Use `| ~/bin/pi --cli` not `> /dev/null` |
| Tests fail on `hardware` suite | User not in audio group | `sudo usermod -aG audio $USER` then logout/login |

### Debug Mode

```bash
# Enable verbose logging
export RUST_LOG=debug
voxtype --push-to-talk 2>&1 | tee /tmp/voxtype-debug.log

# Check ALSA permissions
arecord -v -f cd -d 2 /tmp/alsa-test.wav 2>&1 | grep -i error
```

### Performance Tuning

```toml
# ~/.config/voxtype/config.toml

[performance]
# Use GPU acceleration if available (NVIDIA CUDA)
use_cuda = true
# Number of CPU threads for transcription
threads = 4
# Batch size for audio processing
batch_size = 16
```

---

## Security Considerations

### Command Injection Prevention

Voice input is sanitized before reaching pi agent:

- Shell metacharacters (`;`, `|`, `&`, `$`) are escaped
- Null bytes are stripped
- ANSI escape sequences are filtered
- Maximum input length: 64KB

### Audit Logging

All voice commands are logged to:

```bash
~/.pi/voice-commands.log
# Format: TIMESTAMP | TRANSCRIPTION | USER | SESSION_ID
```

Review periodically:

```bash
# Last 50 voice commands
tail -50 ~/.pi/voice-commands.log

# Search for specific commands
grep -i "BTC" ~/.pi/voice-commands.log
```

### Best Practices

1. **Never** speak sensitive data (API keys, passwords, seed phrases)
2. **Always** verify transcribed command before execution (use `--dry-run` if available)
3. **Review** voice command logs weekly
4. **Restrict** voice input to trusted environments (no public spaces)

---

## Repository

**Source:** [`carlosfrias/voice-input-acceptance-tests`](https://github.com/carlosfrias/voice-input-acceptance-tests) (private)

```bash
# Clone the test suite
git clone git@github.com:carlosfrias/voice-input-acceptance-tests.git
cd voice-input-acceptance-tests

# Run tests
./scripts/run-all.sh --verbose
```

---

## Related Documentation

- [`acceptance-testing.md`](../acceptance-testing.md) — General acceptance testing framework
- [`testing-harness.md`](../testing-harness.md) — Test runner architecture
- [`tools/voxtype.md`](../tools/voxtype.md) — Voxtype tool reference
- [`operational/voice-input-backlog.md`](../operational/voice-input-backlog.md) — Feature backlog

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-10 | 1.0.0 | Initial release with 7 test suites |
| 2026-05-10 | 1.0.1 | Added security test suite, CI workflow |
