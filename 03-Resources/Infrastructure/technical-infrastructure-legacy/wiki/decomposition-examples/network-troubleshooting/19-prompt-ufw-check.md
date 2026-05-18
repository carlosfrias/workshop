# Sub-Task 19: Check ufw Status

## Instruction

Execute `ufw status verbose` and determine if ufw (Uncomplicated Firewall) is active and blocking outbound traffic.

## Command to Execute

```bash
sudo ufw status verbose
```

## Expected Output Format

```json
{
  "task": "ufw_check",
  "active": false,
  "status": "inactive",
  "blocking_outbound": false,
  "raw_output": "Status: inactive",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `active` is boolean (true if status is "active")
- [ ] `status` is either "active" or "inactive"
- [ ] `blocking_outbound` is boolean (true if outbound is denied)
- [ ] `raw_output` contains the full ufw status output
- [ ] JSON is valid and parseable

## Decision Logic

- `active = true` if output contains "Status: active"
- `blocking_outbound = true` if output contains "DENY OUT" or "deny out"

## Example: UFW Inactive (Not Blocking)

```json
{
  "task": "ufw_check",
  "active": false,
  "status": "inactive",
  "blocking_outbound": false,
  "raw_output": "Status: inactive",
  "exit_code": 0
}
```

## Example: UFW Active, Not Blocking Outbound

```json
{
  "task": "ufw_check",
  "active": true,
  "status": "active",
  "blocking_outbound": false,
  "raw_output": "Status: active\nLogging: on (low)\nDefault: deny (incoming), allow (outgoing), deny (routed)\n...",
  "exit_code": 0
}
```

## Example: UFW Active, Blocking Outbound

```json
{
  "task": "ufw_check",
  "active": true,
  "status": "active",
  "blocking_outbound": true,
  "raw_output": "Status: active\n\nTo                         Action      From\n--                         ------      ----\nAnywhere                   DENY OUT    Anywhere",
  "exit_code": 0
}
```

## Notes

- ufw is a frontend for iptables/nftables
- "Default: allow (outgoing)" = not blocking even if active
