# Sub-Task 6: Parse Internet Ping Result

## Instruction

Parse the raw ping output from Sub-Task 5 and extract the metrics. Do NOT execute any commands — only parse the provided output.

## Input

- Raw ping output from Sub-Task 5 (in `raw_output` field)

## Parsing Rules

1. **Success**: If any "64 bytes from" lines appear, success = true
2. **Packet loss**: Extract the percentage from "X% packet loss"

## Expected Output Format

```json
{
  "task": "ping_internet_parse",
  "success": true,
  "packets_sent": 3,
  "packets_received": 3,
  "packet_loss_percent": 0,
  "error_message": null
}
```

## Verification Criteria

- [ ] `success` is boolean (true if any replies received)
- [ ] `packet_loss_percent` is a number (0-100)
- [ ] `error_message` is null on success, or contains error text on failure
- [ ] JSON is valid and parseable

## Example: Success

```json
{
  "task": "ping_internet_parse",
  "success": true,
  "packets_sent": 3,
  "packets_received": 3,
  "packet_loss_percent": 0,
  "error_message": null
}
```

## Example: Failure (Driver Issue)

```json
{
  "task": "ping_internet_parse",
  "success": false,
  "packets_sent": 3,
  "packets_received": 0,
  "packet_loss_percent": 100,
  "error_message": "100% packet loss"
}
```

## Notes

- Only parse — do NOT execute any commands
- If gateway ping succeeded (Sub-Task 4) but this shows 100% loss, suspect driver issue
