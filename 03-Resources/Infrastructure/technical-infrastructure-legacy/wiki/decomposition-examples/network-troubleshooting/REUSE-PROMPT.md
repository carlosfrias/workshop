# Prompt: Create Decomposition Example for Network Troubleshooting

## Context

You are setting up the **decompose-execute-verify** pattern for network troubleshooting on a new node. This enables cost-optimized execution where:
- Cloud model (qwen3.5:cloud) decomposes complex tasks
- Local model (qwen3:4b) executes atomic sub-tasks
- Cloud model verifies outputs before they become authoritative

## Task

Create a complete decomposition example for the network troubleshooting playbook, including:
1. A decomposition plan with all sub-tasks
2. Individual prompt files for each sub-task
3. A download script for transferring to other nodes
4. GitHub Gists for distribution

## Source Files

Read these files first:
- `./technical-infrastructure/prompts/network-troubleshooting.md` — The playbook to decompose
- `./.pi/agents/decomposer.md` — Decomposer agent definition and output format
- `./technical-infrastructure/wiki/decompose-execute-verify-pattern.md` — Pattern documentation

## Step 1: Create Decomposition Plan

Create a file at:
```
./technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/00-decomposition-plan.md
```

This file must include:
- **Overview** — 1-2 sentence summary
- **Source Document** — Path to the playbook
- **Target Model** — qwen3:4b for local execution
- **Sub-Tasks Table** — All diagnostic and repair steps with:
  - Task number and name
  - Target agent (worker/verifier)
  - Rationale for decomposition
  - Expected output format
- **Dependencies** — Which tasks depend on others
- **Verification Criteria** — What the verifier checks for each task
- **Token Budget** — Estimated tokens and cost comparison vs. end-to-end cloud

## Step 2: Create Prompt Files

For each sub-task in the decomposition plan, create a prompt file:

```
./technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/01-prompt-<name>.md
./technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/02-prompt-<name>.md
...
```

Each prompt file must include:
- **Instruction** — The exact prompt to send to qwen3:4b
- **Input** — What data this step needs from previous steps
- **Command to Execute** — Shell commands (if applicable)
- **Expected Output Format** — JSON schema or markdown template
- **Verification Criteria** — Checklist for the verifier
- **Diagnostic Significance** — What the result means (if applicable)
- **Examples** — Success and failure cases with sample output

### Required Sub-Tasks

| # | Prompt File | Purpose | Model |
|---|-------------|---------|-------|
| 1 | `01-prompt-extract-commands.md` | Extract all commands from playbook | qwen3:4b |
| 2 | `02-prompt-ping-gateway.md` | Test gateway connectivity | qwen3:4b |
| 3 | `03-prompt-ping-internet.md` | Test internet (8.8.8.8) | qwen3:4b |
| 4 | `04-prompt-check-dns.md` | Test DNS resolution | qwen3:4b |
| 5 | `05-prompt-identify-interface.md` | Identify NIC, driver, MAC | qwen3:4b |
| 6 | `06-prompt-check-driver.md` | Check for r8169 driver | qwen3:4b |
| 7 | `07-prompt-tcpdump.md` | Verify packets leaving interface | qwen3:4b |
| 8 | `08-prompt-firewall-check.md` | Check iptables/nft/ufw | qwen3:4b |
| 9 | `09-prompt-decision-driver-fix.md` | **Decision: apply fix?** | qwen3.5:cloud |
| 10 | `10-prompt-apply-fix.md` | Install r8168-dkms, switch drivers | qwen3:4b |
| 11 | `11-prompt-log-incident.md` | Log to wiki | qwen3:4b |

## Step 3: Create Download Script

Create a bash script for transferring files to other nodes:

```
./download-decomposition.sh
```

The script must:
1. Create a tar.gz archive of the decomposition directory
2. Base64-encode the archive (for safe transfer)
3. Provide instructions for creating a GitHub Gist
4. Include a decode/extract command for the target node

Example structure:
```bash
#!/bin/bash
# Archive the files
tar -czvf network-troubleshooting-decomposition.tar.gz \
    technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/

# Encode for transfer
base64 -i network-troubleshooting-decomposition.tar.gz \
    -o network-troubleshooting-decomposition.tar.gz.b64

# Print instructions for Gist upload
echo "Upload to Gist:"
echo "  gh gist create network-troubleshooting-decomposition.tar.gz.b64 --desc \"...\" --public"
```

## Step 4: Create Distribution Gists

Create three GitHub Gists:

### Gist 1: Archive
```bash
gh gist create network-troubleshooting-decomposition.tar.gz.b64 \
    --desc "Network troubleshooting decomposition prompts for <node-name>" \
    --public
```

### Gist 2: Download Script
```bash
gh gist create download-decomposition.sh \
    --desc "Download script for network troubleshooting decomposition prompts" \
    --public
```

### Gist 3: Instructions
Create `DECODE-INSTRUCTIONS.md` with:
- Download commands (script and manual)
- File listing with descriptions
- Usage examples
- Background on the pattern

```bash
gh gist create DECODE-INSTRUCTIONS.md \
    --desc "Instructions for downloading network troubleshooting decomposition prompts" \
    --public
```

### Add Comment to Archive Gist
Post the download instructions as a comment on Gist 1:
```bash
gh api gists/<gist-id>/comments -X POST -f body='...'
```

## Step 5: Commit to Repository

Commit all local files:
```bash
git add technical-infrastructure/wiki/decomposition-examples/network-troubleshooting/
git add download-decomposition.sh DECODE-INSTRUCTIONS.md
git commit -m "Add network troubleshooting decomposition example for <node-name>

- 12 prompt files for decompose-execute-verify pattern
- Download script and distribution gists
- Target: qwen3:4b for local execution

Gists:
- Archive: <URL>
- Script: <URL>
- Instructions: <URL>"
git push origin main
```

## Output Deliverables

After completion, provide:

1. **Directory path** — Where the prompt files are located
2. **File count** — Number of files created
3. **Gist URLs** — All three gists for distribution
4. **Commit hash** — For repository tracking
5. **Token budget** — Estimated cost savings vs. end-to-end cloud

## Quality Checks

Before finishing, verify:
- [ ] All 12 prompt files exist and are non-empty
- [ ] Each prompt has: Instruction, Input, Output Format, Verification Criteria, Examples
- [ ] Sub-task 9 (decision) is marked for cloud execution
- [ ] Download script works when tested locally
- [ ] All three gists are created and public
- [ ] Comment posted to archive gist with download instructions
- [ ] Files committed and pushed to repository

## Adaptation for Other Nodes

When repeating this for other nodes (node2, node3, etc.):
1. Update node-specific details (MAC address, interface name)
2. Adjust prompts if the node has different hardware (e.g., different NIC chipset)
3. Create new gists with node-specific descriptions
4. Update the incident log template with the correct node identifier

---

**Created:** 2026-04-24  
**Source Node:** fnet2 (node1)  
**Pattern:** decompose-execute-verify  
**Target Model:** qwen3:4b (local), qwen3.5:cloud (decision/verify)
