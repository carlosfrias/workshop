# Sub-Task 17: Check iptables Rules

## Instruction

Execute `iptables -L -n -v` and determine if any rules are blocking outbound traffic.

## Command to Execute

```bash
sudo iptables -L -n -v
```

## Expected Output Format

```json
{
  "task": "iptables_check",
  "has_rules": false,
  "blocking_outbound": false,
  "rule_count": 3,
  "raw_output": "Chain INPUT (policy ACCEPT)\nChain FORWARD (policy ACCEPT)\nChain OUTPUT (policy ACCEPT)...",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `has_rules` is boolean (true if any rules beyond default chains)
- [ ] `blocking_outbound` is boolean (true if OUTPUT chain has DROP/REJECT)
- [ ] `rule_count` is a non-negative integer
- [ ] `raw_output` contains the full iptables output
- [ ] JSON is valid and parseable

## Decision Logic

- `has_rules = true` if there are any user-defined chains or rules in INPUT/OUTPUT/FORWARD
- `blocking_outbound = true` if OUTPUT chain contains DROP or REJECT rules
- `rule_count` = count of non-empty lines in OUTPUT chain

## Example: No Blocking (Default Policy ACCEPT)

```json
{
  "task": "iptables_check",
  "has_rules": false,
  "blocking_outbound": false,
  "rule_count": 0,
  "raw_output": "Chain INPUT (policy ACCEPT)\nChain FORWARD (policy ACCEPT)\nChain OUTPUT (policy ACCEPT)",
  "exit_code": 0
}
```

## Example: Blocking Rule Present

```json
{
  "task": "iptables_check",
  "has_rules": true,
  "blocking_outbound": true,
  "rule_count": 1,
  "raw_output": "Chain INPUT (policy ACCEPT)\nChain FORWARD (policy ACCEPT)\nChain OUTPUT (policy DROP)\ntarget     prot opt source               destination\nDROP       all  --  0.0.0.0/0            0.0.0.0/0",
  "exit_code": 0
}
```

## Notes

- Policy ACCEPT with no rules = not blocking
- Policy DROP in OUTPUT chain = blocking
