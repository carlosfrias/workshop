# Sub-Task 20: Aggregate Firewall Results

## Instruction

Combine the results from Sub-Tasks 17, 18, and 19 to determine if ANY firewall is blocking outbound traffic.

## Input

- Results from Sub-Task 17 (iptables): `blocking_outbound` boolean
- Results from Sub-Task 18 (nftables): `blocking_outbound` boolean
- Results from Sub-Task 19 (ufw): `blocking_outbound` boolean

## Decision Logic

```
firewall_blocking = (iptables.blocking OR nftables.blocking OR ufw.blocking)
```

## Expected Output Format

```json
{
  "task": "firewall_aggregate",
  "iptables_blocking": false,
  "nftables_blocking": false,
  "ufw_blocking": false,
  "firewall_blocking": false,
  "blocking_source": null
}
```

## Verification Criteria

- [ ] `firewall_blocking` is boolean (true if ANY of the three is blocking)
- [ ] `blocking_source` is null (if none blocking) or name of blocking firewall ("iptables", "nftables", or "ufw")
- [ ] JSON is valid and parseable

## Example: No Blocking

```json
{
  "task": "firewall_aggregate",
  "iptables_blocking": false,
  "nftables_blocking": false,
  "ufw_blocking": false,
  "firewall_blocking": false,
  "blocking_source": null
}
```

## Example: UFW Blocking

```json
{
  "task": "firewall_aggregate",
  "iptables_blocking": false,
  "nftables_blocking": false,
  "ufw_blocking": true,
  "firewall_blocking": true,
  "blocking_source": "ufw"
}
```

## Notes

- Only one firewall should be active at a time
- If multiple report blocking, list the first one found in `blocking_source`
