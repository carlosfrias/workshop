# Sub-Task 24: Unload r8169 Driver

## Instruction

Execute `sudo modprobe -r r8169` to unload the buggy driver from the kernel.

## Command to Execute

```bash
sudo modprobe -r r8169
```

## Expected Output Format

```json
{
  "task": "fix_unload_r8169",
  "step": 3,
  "success": true,
  "raw_output": "",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `success` is boolean (true if exit_code is 0)
- [ ] `raw_output` is typically empty on success (modprobe is silent)
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] `step` is 3 (third step in fix procedure)
- [ ] JSON is valid and parseable

## Example: Success

```json
{
  "task": "fix_unload_r8169",
  "step": 3,
  "success": true,
  "raw_output": "",
  "exit_code": 0
}
```

## Example: Failure (Module In Use)

```json
{
  "task": "fix_unload_r8169",
  "step": 3,
  "success": false,
  "raw_output": "modprobe: FATAL: Module r8169 is in use.",
  "exit_code": 1
}
```

## Notes

- modprobe is typically silent on success (empty output)
- If "module is in use", the interface may need to be brought down first
- If this fails, a reboot may be required after installation
