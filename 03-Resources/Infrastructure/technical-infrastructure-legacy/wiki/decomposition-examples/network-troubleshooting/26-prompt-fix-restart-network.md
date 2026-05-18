# Sub-Task 26: Restart NetworkManager

## Instruction

Execute `sudo systemctl restart NetworkManager` to restart the network management service and apply the new driver.

## Command to Execute

```bash
sudo systemctl restart NetworkManager
```

## Expected Output Format

```json
{
  "task": "fix_restart_network",
  "step": 5,
  "success": true,
  "raw_output": "",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `success` is boolean (true if exit_code is 0)
- [ ] `raw_output` is typically empty on success (systemctl is silent)
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] `step` is 5 (fifth step in fix procedure)
- [ ] JSON is valid and parseable

## Example: Success

```json
{
  "task": "fix_restart_network",
  "step": 5,
  "success": true,
  "raw_output": "",
  "exit_code": 0
}
```

## Example: Failure (Service Not Found)

```json
{
  "task": "fix_restart_network",
  "step": 5,
  "success": false,
  "raw_output": "Failed to restart NetworkManager.service: Unit NetworkManager.service not found.",
  "exit_code": 5
}
```

## Notes

- systemctl is typically silent on success (empty output)
- NetworkManager may take a few seconds to reinitialize the interface
- Wait 5 seconds after this command before testing connectivity
