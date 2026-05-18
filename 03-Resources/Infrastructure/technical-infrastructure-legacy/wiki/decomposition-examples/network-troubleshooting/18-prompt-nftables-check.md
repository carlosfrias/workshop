# Sub-Task 18: Check nftables Rules

## Instruction

Execute `nft list ruleset` and determine if any nftables rules are blocking outbound traffic.

## Command to Execute

```bash
sudo nft list ruleset
```

## Expected Output Format

```json
{
  "task": "nftables_check",
  "has_rules": false,
  "blocking_outbound": false,
  "rule_count": 0,
  "raw_output": "",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `has_rules` is boolean (true if ruleset is non-empty)
- [ ] `blocking_outbound` is boolean (true if drop/reject rules for outgoing)
- [ ] `rule_count` is a non-negative integer
- [ ] `raw_output` contains the full nft output (or empty string if no rules)
- [ ] JSON is valid and parseable

## Decision Logic

- `has_rules = true` if output is non-empty
- `blocking_outbound = true` if output contains "drop" or "reject" for outgoing traffic
- `rule_count` = count of lines containing "drop" or "reject"

## Example: No Rules (Empty Ruleset)

```json
{
  "task": "nftables_check",
  "has_rules": false,
  "blocking_outbound": false,
  "rule_count": 0,
  "raw_output": "",
  "exit_code": 0
}
```

## Example: Rules Present But Not Blocking

```json
{
  "task": "nftables_check",
  "has_rules": true,
  "blocking_outbound": false,
  "rule_count": 0,
  "raw_output": "table inet filter {\n    chain input {\n        type filter hook input priority 0; policy accept;\n    }\n}",
  "exit_code": 0
}
```

## Notes

- Empty output = no nftables rules = not blocking
- nftables is the newer replacement for iptables
