# Sub-Task 11: Get Driver Info

## Instruction

Execute `ethtool -i` on the primary interface to get driver information. Extract the driver name and version.

## Input

- Interface name from Sub-Task 10 (e.g., `enp7s0`)

## Command to Execute

```bash
ethtool -i <interface_name>
```

## Expected Output Format

```json
{
  "task": "get_driver_info",
  "interface": "enp7s0",
  "driver_name": "r8169",
  "driver_version": "5.15.0-generic",
  "firmware_version": "rtl8168h-2_0.0.2",
  "raw_output": "driver: r8169\nversion: 5.15.0-generic\nfirmware-version: rtl8168h-2_0.0.2\n...",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `driver_name` is extracted from the output
- [ ] `driver_version` is extracted (or null if not present)
- [ ] `firmware_version` is extracted (or null if not present)
- [ ] `raw_output` contains the full ethtool output
- [ ] JSON is valid and parseable

## Example Output

```json
{
  "task": "get_driver_info",
  "interface": "enp7s0",
  "driver_name": "r8169",
  "driver_version": "5.15.0-generic",
  "firmware_version": "rtl8168h-2_0.0.2",
  "raw_output": "driver: r8169\nversion: 5.15.0-generic\nfirmware-version: rtl8168h-2_0.0.2\nbus-info: 0000:07:00.0",
  "exit_code": 0
}
```

## Notes

- If ethtool is not installed, report: `{"error": "ethtool not found"}`
- Driver name is critical for diagnosing r8169 vs r8168 issue
