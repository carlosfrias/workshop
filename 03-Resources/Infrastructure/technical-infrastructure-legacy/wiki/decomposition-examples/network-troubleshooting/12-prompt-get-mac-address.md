# Sub-Task 12: Get MAC Address

## Instruction

Execute `ip link show` on the primary interface and extract the MAC address.

## Input

- Interface name from Sub-Task 10 (e.g., `enp7s0`)

## Command to Execute

```bash
ip link show <interface_name>
```

## Expected Output Format

```json
{
  "task": "get_mac_address",
  "interface": "enp7s0",
  "mac_address": "0C:9D:92:CC:55:4C",
  "raw_output": "2: enp7s0: <BROADCAST,MULTICAST,UP,LOWER_UP> ... link/ether 0c:9d:92:cc:55:4c brd ff:ff:ff:ff:ff:ff",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `mac_address` is in standard format (XX:XX:XX:XX:XX:XX, uppercase)
- [ ] `raw_output` contains the full `ip link` output
- [ ] `exit_code` is 0 (success)
- [ ] JSON is valid and parseable

## Example Output

```json
{
  "task": "get_mac_address",
  "interface": "enp7s0",
  "mac_address": "0C:9D:92:CC:55:4C",
  "raw_output": "2: enp7s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DORMANT group default qlen 1000\n    link/ether 0c:9d:92:cc:55:4c brd ff:ff:ff:ff:ff:ff",
  "exit_code": 0
}
```

## Notes

- Convert MAC to uppercase for consistency
- MAC address appears after `link/ether` in the output
