# Sub-Task 8: Parse DNS Resolution Result

## Instruction

Parse the raw ping output from Sub-Task 7 and determine if DNS resolution worked. Do NOT execute any commands — only parse the provided output.

## Input

- Raw ping output from Sub-Task 7 (in `raw_output` field)

## Parsing Rules

1. **DNS works**: If output contains an IP address in parentheses like `google.com (142.250.185.46)`, DNS resolved successfully
2. **DNS fails**: If output contains "Temporary failure in name resolution" or similar error

## Expected Output Format

```json
{
  "task": "dns_parse",
  "dns_works": true,
  "resolved_ip": "142.250.185.46",
  "ping_success": true,
  "error_message": null
}
```

## Verification Criteria

- [ ] `dns_works` is boolean (true if IP was resolved)
- [ ] `resolved_ip` is the IP address (or null if DNS failed)
- [ ] `ping_success` is boolean (true if any replies received)
- [ ] `error_message` is null on success, or contains error text on failure
- [ ] JSON is valid and parseable

## Example: DNS Works

```json
{
  "task": "dns_parse",
  "dns_works": true,
  "resolved_ip": "142.250.185.46",
  "ping_success": true,
  "error_message": null
}
```

## Example: DNS Fails

```json
{
  "task": "dns_parse",
  "dns_works": false,
  "resolved_ip": null,
  "ping_success": false,
  "error_message": "Temporary failure in name resolution"
}
```

## Notes

- Only parse — do NOT execute any commands
- Extract the IP from parentheses if present
