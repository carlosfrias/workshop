# Sub-Task 28: Aggregate Fix Results

## Instruction

Combine the results from Sub-Tasks 22-27 to determine if the driver fix was successfully applied and connectivity was restored.

## Input

- Sub-Task 22 (apt update): `success` boolean
- Sub-Task 23 (install driver): `success` boolean
- Sub-Task 24 (unload r8169): `success` boolean
- Sub-Task 25 (load r8168): `success` boolean
- Sub-Task 26 (restart NetworkManager): `success` boolean
- Sub-Task 27 (verify ping): `success` boolean, `packet_loss_percent` number

## Decision Logic

```
fix_applied = (step22.success AND step23.success AND step24.success AND step25.success AND step26.success)
connectivity_restored = step27.success AND step27.packet_loss_percent == 0
overall_success = fix_applied AND connectivity_restored
```

## Expected Output Format

```json
{
  "task": "fix_aggregate",
  "steps": {
    "apt_update": true,
    "install_driver": true,
    "unload_r8169": true,
    "load_r8168": true,
    "restart_network": true,
    "verify_ping": true
  },
  "fix_applied": true,
  "connectivity_restored": true,
  "overall_success": true,
  "packet_loss_before": 100,
  "packet_loss_after": 0,
  "failed_step": null
}
```

## Verification Criteria

- [ ] `fix_applied` is boolean (true if steps 22-26 all succeeded)
- [ ] `connectivity_restored` is boolean (true if step 27 succeeded with 0% loss)
- [ ] `overall_success` is boolean (true if both fix_applied AND connectivity_restored)
- [ ] `failed_step` is null (if all succeeded) or name of first failed step
- [ ] JSON is valid and parseable

## Example: Complete Success

```json
{
  "task": "fix_aggregate",
  "steps": {
    "apt_update": true,
    "install_driver": true,
    "unload_r8169": true,
    "load_r8168": true,
    "restart_network": true,
    "verify_ping": true
  },
  "fix_applied": true,
  "connectivity_restored": true,
  "overall_success": true,
  "packet_loss_before": 100,
  "packet_loss_after": 0,
  "failed_step": null
}
```

## Example: Fix Applied But Connectivity Not Restored

```json
{
  "task": "fix_aggregate",
  "steps": {
    "apt_update": true,
    "install_driver": true,
    "unload_r8169": true,
    "load_r8168": true,
    "restart_network": true,
    "verify_ping": false
  },
  "fix_applied": true,
  "connectivity_restored": false,
  "overall_success": false,
  "packet_loss_before": 100,
  "packet_loss_after": 100,
  "failed_step": "verify_ping"
}
```

## Notes

- `fix_applied` means all installation steps completed
- `connectivity_restored` means ping test succeeded
- Both must be true for `overall_success`
