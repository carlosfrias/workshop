# Decomposition Plan: Network Troubleshooting Playbook

## Overview

Break down the network troubleshooting playbook into **fine-grained atomic** diagnostic and repair steps that qwen3:4b can execute sequentially. Each sub-task performs **one operation only** (one command OR one parsing operation). This ensures reliable execution on smaller models.

## Source Document

- **File:** `./technical-infrastructure/prompts/network-troubleshooting.md`
- **Target Model:** `ollama/qwen3:4b` (local execution)
- **Verifier:** `ollama/qwen3.5:cloud` (validation)

## Sub-Tasks (29 total)

| # | Task | Target Agent | Rationale | Expected Output |
|---|------|--------------|-----------|-----------------|
| 1 | Extract diagnostic commands from Quick Diagnosis section | worker | Simple text extraction | List of 5 commands |
| 2 | Extract commands from What to Rule Out table | worker | Simple text extraction | List of 9 commands |
| 3 | Execute ping to gateway | worker | Single command | Raw ping output |
| 4 | Parse ping gateway result | worker | Extract metrics from output | JSON: success, packet_loss, latency |
| 5 | Execute ping to 8.8.8.8 | worker | Single command | Raw ping output |
| 6 | Parse ping internet result | worker | Extract metrics from output | JSON: success, packet_loss |
| 7 | Execute ping to google.com | worker | Single command | Raw ping output |
| 8 | Parse DNS resolution result | worker | Check if hostname resolved | JSON: dns_works, resolved_ip |
| 9 | List network interfaces | worker | Run `ip addr show` | Raw output |
| 10 | Identify primary interface from default route | worker | Run `ip route \| grep default` | Interface name |
| 11 | Get driver info for primary interface | worker | Run `ethtool -i <iface>` | Driver name, version |
| 12 | Get MAC address for primary interface | worker | Run `ip link show <iface>` | MAC address |
| 13 | Check if r8169 module is loaded | worker | Run `lsmod \| grep r8169` | Boolean: present/absent |
| 14 | Check if r8168 module is loaded | worker | Run `lsmod \| grep r8168` | Boolean: present/absent |
| 15 | Run tcpdump to capture outbound packets | worker | Run tcpdump for 5 seconds | Raw tcpdump output |
| 16 | Analyze tcpdump: count outbound vs inbound | worker | Parse tcpdump output | JSON: outbound_count, inbound_count, pattern |
| 17 | Check iptables rules | worker | Run `iptables -L -n -v` | JSON: has_rules, blocking |
| 18 | Check nftables rules | worker | Run `nft list ruleset` | JSON: has_rules, blocking |
| 19 | Check ufw status | worker | Run `ufw status verbose` | JSON: active, blocking |
| 20 | Aggregate firewall results | worker | Combine 17-19 | JSON: firewall_blocking |
| 21 | Determine if driver fix is needed | verifier | Decision based on 4,6,8,11-14,16,20 | Boolean + rationale |
| 22 | Execute: apt update | worker | Single command | Success/failure |
| 23 | Execute: install r8168-dkms | worker | Single command | Success/failure |
| 24 | Execute: modprobe -r r8169 | worker | Single command | Success/failure |
| 25 | Execute: modprobe r8168 | worker | Single command | Success/failure |
| 26 | Execute: restart NetworkManager | worker | Single command | Success/failure |
| 27 | Verify connectivity post-fix | worker | Run ping 8.8.8.8 | JSON: success, packet_loss |
| 28 | Aggregate fix results | worker | Combine 22-27 | JSON: fix_applied, connectivity_restored |
| 29 | Log incident to wiki | worker | Write markdown file | File path + summary |

## Dependencies

- **Independent (parallel execution):** Tasks 1-2, 3-4, 5-6, 7-8, 9-12, 13-14, 15-16, 17-19
- **Depends on 17-19:** Task 20 (aggregation)
- **Depends on 4,6,8,11-14,16,20:** Task 21 (decision requires all diagnostic results)
- **Depends on 21:** Tasks 22-27 (only execute fix if decision is "yes")
- **Depends on 22-27:** Task 28 (aggregation)
- **Depends on 28:** Task 29 (log after fix is applied)

## Verification Criteria

| Sub-Task | What Verifier Checks |
|----------|----------------------|
| 1-2 | All commands from playbook are extracted, none missing |
| 3-4 | Ping command executed, output parsed correctly, metrics accurate |
| 5-6 | Ping command executed, packet loss calculated correctly |
| 7-8 | DNS resolution check accurate, IP extracted if resolved |
| 9-10 | Interface identification matches system state |
| 11 | Driver name extracted correctly from ethtool output |
| 12 | MAC address in correct format (XX:XX:XX:XX:XX:XX) |
| 13-14 | Module detection accurate (no false positives/negatives) |
| 15-16 | tcpdump output parsed, outbound/inbound counted correctly |
| 17-19 | Each firewall system checked independently |
| 20 | Aggregation logic correct (any blocking = true) |
| 21 | Decision logic matches playbook rules (7 conditions) |
| 22-27 | Each command executed in order, errors reported |
| 28 | Fix status and connectivity restoration accurate |
| 29 | Log entry includes all required fields |

## Token Budget

| Step | Model | Est. Tokens | Cost |
|------|-------|-------------|------|
| Decomposition (this file) | qwen3.5:cloud | ~2KB | ~$0.06 |
| Tasks 1-20 (local) | qwen3:4b | ~6KB total | ~$0.00 |
| Task 21 (decision) | qwen3.5:cloud | ~1.5KB | ~$0.045 |
| Tasks 22-28 (local) | qwen3:4b | ~3KB total | ~$0.00 |
| Task 29 (log) | qwen3:4b | ~1KB | ~$0.00 |
| Verification (all) | qwen3.5:cloud | ~3KB | ~$0.09 |
| **Total** | | **~16.5KB** | **~$0.195** |

**Comparison:** End-to-end cloud execution would cost ~$0.35 (more tokens for retries). This pattern saves ~44% while improving reliability on small models.

## Files Created

| # | File | Purpose |
|---|------|---------|
| 00 | `00-decomposition-plan.md` | This file — overview and task table (29 tasks) |
| 01 | `01-prompt-extract-commands-quick.md` | Sub-task 1: Extract Quick Diagnosis commands |
| 02 | `02-prompt-extract-commands-ruleout.md` | Sub-task 2: Extract What to Rule Out commands |
| 03 | `03-prompt-ping-gateway-exec.md` | Sub-task 3: Execute gateway ping |
| 04 | `04-prompt-ping-gateway-parse.md` | Sub-task 4: Parse gateway ping result |
| 05 | `05-prompt-ping-internet-exec.md` | Sub-task 5: Execute internet ping |
| 06 | `06-prompt-ping-internet-parse.md` | Sub-task 6: Parse internet ping result |
| 07 | `07-prompt-dns-exec.md` | Sub-task 7: Execute DNS ping |
| 08 | `08-prompt-dns-parse.md` | Sub-task 8: Parse DNS result |
| 09 | `09-prompt-list-interfaces.md` | Sub-task 9: List all interfaces |
| 10 | `10-prompt-get-primary-interface.md` | Sub-task 10: Identify primary interface |
| 11 | `11-prompt-get-driver-info.md` | Sub-task 11: Get driver info |
| 12 | `12-prompt-get-mac-address.md` | Sub-task 12: Get MAC address |
| 13 | `13-prompt-check-r8169.md` | Sub-task 13: Check r8169 loaded |
| 14 | `14-prompt-check-r8168.md` | Sub-task 14: Check r8168 loaded |
| 15 | `15-prompt-tcpdump-capture.md` | Sub-task 15: Capture packets |
| 16 | `16-prompt-tcpdump-analyze.md` | Sub-task 16: Analyze packet capture |
| 17 | `17-prompt-iptables-check.md` | Sub-task 17: Check iptables |
| 18 | `18-prompt-nftables-check.md` | Sub-task 18: Check nftables |
| 19 | `19-prompt-ufw-check.md` | Sub-task 19: Check ufw |
| 20 | `20-prompt-firewall-aggregate.md` | Sub-task 20: Aggregate firewall results |
| 21 | `21-prompt-decision-driver-fix.md` | Sub-task 21: Decision logic |
| 22 | `22-prompt-fix-apt-update.md` | Sub-task 22: apt update |
| 23 | `23-prompt-fix-install-driver.md` | Sub-task 23: install r8168-dkms |
| 24 | `24-prompt-fix-unload-r8169.md` | Sub-task 24: unload r8169 |
| 25 | `25-prompt-fix-load-r8168.md` | Sub-task 25: load r8168 |
| 26 | `26-prompt-fix-restart-network.md` | Sub-task 26: restart NetworkManager |
| 27 | `27-prompt-fix-verify-ping.md` | Sub-task 27: verify connectivity |
| 28 | `28-prompt-fix-aggregate.md` | Sub-task 28: Aggregate fix results |
| 29 | `29-prompt-log-incident.md` | Sub-task 29: Log to wiki |

---

## Design Principles for qwen3:4b

1. **One operation per task** — Either execute ONE command OR parse ONE output, never both
2. **Raw output separation** — Command execution and parsing are separate tasks
3. **Aggregation tasks** — Combine multiple results in a dedicated task (not during parsing)
4. **Decision isolation** — All reasoning happens in cloud model (task 21)
5. **Explicit dependencies** — Each task knows what inputs it needs

## Why 29 Tasks Instead of 11?

| Original 11-task | Problem for qwen3:4b | New approach |
|------------------|---------------------|--------------|
| "Ping gateway and parse result" | Two operations in one prompt | Task 3 (exec) + Task 4 (parse) |
| "Identify interface and driver" | Multiple commands, complex parsing | Tasks 9-12 (separate commands) |
| "Check firewall rules" | Three systems to check | Tasks 17-19 (one per system) + Task 20 (aggregate) |
| "Apply fix" | Six commands with error handling | Tasks 22-27 (one command each) + Task 28 (aggregate) |

**Result:** Each prompt is simple enough for qwen3:4b to execute reliably without confusion or errors.

---

**Next Step:** Examine each prompt file to understand how complex reasoning is broken into fine-grained, atomic instructions suitable for qwen3:4b. Key principle: one command or one parsing operation per task.
