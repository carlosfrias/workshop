# Sub-Task 9: List Network Interfaces

## Instruction

Execute the `ip addr show` command and return the RAW output only. Do NOT parse or interpret — that will be done in Sub-Task 10.

## Command to Execute

```bash
ip addr show
```

## Expected Output Format

```json
{
  "task": "list_interfaces",
  "raw_output": "<exact output from ip addr show>",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `raw_output` contains the actual command output
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] No interpretation or parsing
- [ ] JSON is valid and parseable

## Example Output

```json
{
  "task": "list_interfaces",
  "raw_output": "1: lo: <LOOPBACK,UP,LOWER_UP> ... inet 127.0.0.1/8 scope host lo...\n2: enp7s0: <BROADCAST,MULTICAST,UP,LOWER_UP> ... inet 192.168.0.105/24 brd 192.168.0.255 scope global dynamic enp7s0...\n3: wlo1: <BROADCAST,MULTICAST> ...",
  "exit_code": 0
}
```

## Notes

- Do NOT parse — just capture the output
- Include all interfaces (lo, eth, wlan, etc.)
