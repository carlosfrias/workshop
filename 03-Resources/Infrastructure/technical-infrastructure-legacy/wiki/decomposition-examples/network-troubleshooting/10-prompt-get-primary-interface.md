# Sub-Task 10: Identify Primary Interface

## Instruction

Execute the command to find the default route and extract the interface name. This identifies the primary network interface used for internet connectivity.

## Command to Execute

```bash
ip route | grep default | awk '{print $5}'
```

## Expected Output Format

```json
{
  "task": "get_primary_interface",
  "interface_name": "enp7s0",
  "raw_output": "default via 192.168.0.1 dev enp7s0 proto dhcp src 192.168.0.105 metric 100",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `interface_name` is extracted (e.g., `enp7s0`, `eth0`, `wlan0`)
- [ ] `raw_output` contains the full `ip route` output
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] JSON is valid and parseable

## Example Output

```json
{
  "task": "get_primary_interface",
  "interface_name": "enp7s0",
  "raw_output": "default via 192.168.0.1 dev enp7s0 proto dhcp src 192.168.0.105 metric 100",
  "exit_code": 0
}
```

## Notes

- The interface name is the 5th field in the default route line
- If no default route exists, set `interface_name` to null
