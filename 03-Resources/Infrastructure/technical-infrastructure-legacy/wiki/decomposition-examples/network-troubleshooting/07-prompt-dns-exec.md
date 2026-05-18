# Sub-Task 7: Execute DNS Ping (google.com)

## Instruction

Execute a ping command to google.com (hostname, not IP) and return the RAW output only. Do NOT parse or interpret the results — that will be done in Sub-Task 8.

## Command to Execute

```bash
ping -c 3 google.com
```

## Expected Output Format

```json
{
  "task": "dns_ping_exec",
  "target": "google.com",
  "raw_output": "<exact output from ping command>",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `raw_output` contains the actual ping command output
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] No interpretation or parsing of results
- [ ] JSON is valid and parseable

## Example: DNS Works

```json
{
  "task": "dns_ping_exec",
  "target": "google.com",
  "raw_output": "PING google.com (142.250.185.46) 56(84) bytes of data.\n64 bytes from lga34s36-in-f14.1e100.net (142.250.185.46): icmp_seq=1 ttl=117 time=12.5 ms\n...\n\n--- google.com ping statistics ---\n3 packets transmitted, 3 received, 0% packet loss, time 2003ms",
  "exit_code": 0
}
```

## Example: DNS Fails

```json
{
  "task": "dns_ping_exec",
  "target": "google.com",
  "raw_output": "ping: google.com: Temporary failure in name resolution",
  "exit_code": 2
}
```

## Notes

- Do NOT parse the output — just capture it exactly
- Do NOT determine if DNS works — that's Sub-Task 8
- If output shows an IP in parentheses, DNS resolved successfully
