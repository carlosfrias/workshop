# Sub-Task 3: Execute Gateway Ping

## Instruction

Execute a ping command to the network gateway and return the RAW output only. Do NOT parse or interpret the results — that will be done in Sub-Task 4.

## Input

- Gateway IP: Ask user for their gateway IP (e.g., `192.168.0.1`)
- If unknown, try: `ip route | grep default | awk '{print $3}'` to find it

## Command to Execute

```bash
ping -c 3 <gateway_ip>
```

## Expected Output Format

```json
{
  "task": "ping_gateway_exec",
  "target": "<gateway_ip>",
  "raw_output": "<exact output from ping command>",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `raw_output` contains the actual ping command output
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] No interpretation or parsing of results
- [ ] JSON is valid and parseable

## Example: Success

```json
{
  "task": "ping_gateway_exec",
  "target": "192.168.0.1",
  "raw_output": "PING 192.168.0.1 (192.168.0.1) 56(84) bytes of data.\n64 bytes from 192.168.0.1: icmp_seq=1 ttl=64 time=0.512 ms\n64 bytes from 192.168.0.1: icmp_seq=2 ttl=64 time=0.489 ms\n64 bytes from 192.168.0.1: icmp_seq=3 ttl=64 time=0.501 ms\n\n--- 192.168.0.1 ping statistics ---\n3 packets transmitted, 3 received, 0% packet loss, time 2003ms",
  "exit_code": 0
}
```

## Example: Failure

```json
{
  "task": "ping_gateway_exec",
  "target": "192.168.0.1",
  "raw_output": "PING 192.168.0.1 (192.168.0.1) 56(84) bytes of data.\n\n--- 192.168.0.1 ping statistics ---\n3 packets transmitted, 0 received, 100% packet loss, time 2047ms",
  "exit_code": 1
}
```

## Notes

- Do NOT parse the output — just capture it exactly
- Do NOT determine success/failure — that's Sub-Task 4
- Include the full output including statistics line
