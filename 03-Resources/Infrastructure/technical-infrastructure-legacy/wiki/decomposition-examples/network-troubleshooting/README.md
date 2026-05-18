# Network Troubleshooting Decomposition Prompts (29 Tasks for qwen3:4b)

## Download & Extract on fnet2

### Option A: Run the script (recommended)

```bash
curl -L https://gist.githubusercontent.com/carlosfrias/61911b557e71da88c5e4196fe041c1b1/raw/download-decomposition.sh -o /tmp/download.sh
bash /tmp/download.sh
```

### Option B: Manual commands

```bash
# 1. Download the base64-encoded archive (29-task fine-grained decomposition)
curl -L https://gist.githubusercontent.com/carlosfrias/81a73c4d4b42cae8fadc46d36a73f75f/raw/network-troubleshooting-decomposition.tar.gz.b64 -o /tmp/decomposition.b64

# 2. Decode and extract to home directory
base64 -d /tmp/decomposition.b64 | tar -xzf - -C $HOME

# 3. Verify the files
ls -la ~/technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/
```

## Files Included (29 total)

| # | File | Purpose | Model |
|---|------|---------|-------|
| 00 | `00-decomposition-plan.md` | Overview + 29-task table | — |
| 01 | `01-prompt-extract-commands-quick.md` | Extract Quick Diagnosis commands | qwen3:4b |
| 02 | `02-prompt-extract-commands-ruleout.md` | Extract What to Rule Out commands | qwen3:4b |
| 03 | `03-prompt-ping-gateway-exec.md` | Execute gateway ping | qwen3:4b |
| 04 | `04-prompt-ping-gateway-parse.md` | Parse gateway ping result | qwen3:4b |
| 05 | `05-prompt-ping-internet-exec.md` | Execute internet ping | qwen3:4b |
| 06 | `06-prompt-ping-internet-parse.md` | Parse internet ping result | qwen3:4b |
| 07 | `07-prompt-dns-exec.md` | Execute DNS ping | qwen3:4b |
| 08 | `08-prompt-dns-parse.md` | Parse DNS result | qwen3:4b |
| 09 | `09-prompt-list-interfaces.md` | List all interfaces | qwen3:4b |
| 10 | `10-prompt-get-primary-interface.md` | Identify primary interface | qwen3:4b |
| 11 | `11-prompt-get-driver-info.md` | Get driver info | qwen3:4b |
| 12 | `12-prompt-get-mac-address.md` | Get MAC address | qwen3:4b |
| 13 | `13-prompt-check-r8169.md` | Check r8169 loaded | qwen3:4b |
| 14 | `14-prompt-check-r8168.md` | Check r8168 loaded | qwen3:4b |
| 15 | `15-prompt-tcpdump-capture.md` | Capture packets | qwen3:4b |
| 16 | `16-prompt-tcpdump-analyze.md` | Analyze packet capture | qwen3:4b |
| 17 | `17-prompt-iptables-check.md` | Check iptables | qwen3:4b |
| 18 | `18-prompt-nftables-check.md` | Check nftables | qwen3:4b |
| 19 | `19-prompt-ufw-check.md` | Check ufw | qwen3:4b |
| 20 | `20-prompt-firewall-aggregate.md` | Aggregate firewall results | qwen3:4b |
| 21 | `21-prompt-decision-driver-fix.md` | **Decision: apply fix?** | **qwen3.5:cloud** |
| 22 | `22-prompt-fix-apt-update.md` | apt update | qwen3:4b |
| 23 | `23-prompt-fix-install-driver.md` | Install r8168-dkms | qwen3:4b |
| 24 | `24-prompt-fix-unload-r8169.md` | Unload r8169 | qwen3:4b |
| 25 | `25-prompt-fix-load-r8168.md` | Load r8168 | qwen3:4b |
| 26 | `26-prompt-fix-restart-network.md` | Restart NetworkManager | qwen3:4b |
| 27 | `27-prompt-fix-verify-ping.md` | Verify connectivity | qwen3:4b |
| 28 | `28-prompt-fix-aggregate.md` | Aggregate fix results | qwen3:4b |
| 29 | `29-prompt-log-incident.md` | Log to wiki | qwen3:4b |

## Usage

1. **Start here:** `cat ~/technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/00-decomposition-plan.md`

2. **Test a sub-task:** Copy a prompt file and run it with qwen3:4b:
   ```bash
   pi --model ollama/qwen3:4b "Follow the instructions in ~/technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/03-prompt-ping-gateway-exec.md"
   ```

3. **Full workflow:** Run the decomposition agent with the network-troubleshooting playbook

## Background

These prompts demonstrate the **decompose-execute-verify** pattern with **fine-grained atomic tasks**:

- **Cloud model (qwen3.5:cloud)**: Breaks complex task into 29 atomic sub-tasks
- **Local model (qwen3:4b)**: Executes each sub-task (one command OR one parsing operation)
- **Cloud model (qwen3.5:cloud)**: Verifies outputs before they become authoritative

### Why 29 Tasks Instead of 11?

| Original 11-task approach | Problem for qwen3:4b | New 29-task approach |
|---------------------------|---------------------|---------------------|
| "Ping gateway and parse result" | Two operations in one prompt | Task 3 (exec) + Task 4 (parse) |
| "Identify interface and driver" | Multiple commands, complex parsing | Tasks 9-12 (separate commands) |
| "Check firewall rules" | Three systems to check | Tasks 17-19 (one per system) + Task 20 (aggregate) |
| "Apply fix" | Six commands with error handling | Tasks 22-27 (one command each) + Task 28 (aggregate) |

**Result:** Each prompt is simple enough for qwen3:4b to execute reliably without confusion or errors.

### Token Budget

| Step | Model | Est. Tokens | Cost |
|------|-------|-------------|------|
| Decomposition | qwen3.5:cloud | ~2KB | ~$0.06 |
| Tasks 1-20 (local) | qwen3:4b | ~6KB total | ~$0.00 |
| Task 21 (decision) | qwen3.5:cloud | ~1.5KB | ~$0.045 |
| Tasks 22-28 (local) | qwen3:4b | ~3KB total | ~$0.00 |
| Task 29 (log) | qwen3:4b | ~1KB | ~$0.00 |
| Verification (all) | qwen3.5:cloud | ~3KB | ~$0.09 |
| **Total** | | **~16.5KB** | **~$0.195** |

**Comparison:** End-to-end cloud execution would cost ~$0.35 (more tokens for retries). This pattern saves **~44%** while improving reliability on small models.

---

**Created:** 2026-04-24  
**Pattern:** Fine-grained decompose-execute-verify (29 tasks)  
**Target Model:** qwen3:4b (local), qwen3.5:cloud (decision/verify)  
**Source:** https://github.com/carlosfrias/trading-workspace
