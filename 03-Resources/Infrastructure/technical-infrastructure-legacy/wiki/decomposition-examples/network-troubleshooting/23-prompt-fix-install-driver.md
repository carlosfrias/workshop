# Sub-Task 23: Install r8168-dkms Driver

## Instruction

Execute `sudo apt install -y r8168-dkms` to install the correct driver package.

## Command to Execute

```bash
sudo apt install -y r8168-dkms
```

## Expected Output Format

```json
{
  "task": "fix_install_driver",
  "step": 2,
  "success": true,
  "raw_output": "Reading package lists... Done\nBuilding dependency tree... Done\nSelecting previously unselected package r8168-dkms...\nPreparing to unpack r8168-dkms_8.053.00-1_amd64.deb...\nUnpacking r8168-dkms (8.053.00-1)...\nSetting up r8168-dkms (8.053.00-1)...\nLoading new r8168-8.053.00 DKMS files...\nBuilding module...\nCleaning module...\nDepmod...\nProcessing triggers for initramfs-tools...",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `success` is boolean (true if exit_code is 0)
- [ ] `raw_output` contains the installation output
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] `step` is 2 (second step in fix procedure)
- [ ] JSON is valid and parseable

## Example: Success

```json
{
  "task": "fix_install_driver",
  "step": 2,
  "success": true,
  "raw_output": "Reading package lists... Done\nBuilding dependency tree... Done\nSelecting previously unselected package r8168-dkms...\nSetting up r8168-dkms (8.053.00-1)...\nLoading new r8168-8.053.00 DKMS files...\nBuilding module...\nDepmod...",
  "exit_code": 0
}
```

## Example: Failure (Package Not Found)

```json
{
  "task": "fix_install_driver",
  "step": 2,
  "success": false,
  "raw_output": "Reading package lists... Done\nBuilding dependency tree... Done\nE: Unable to locate package r8168-dkms",
  "exit_code": 100
}
```

## Notes

- This step requires internet connectivity (Sub-Task 22 should have succeeded)
- DKMS will build the module for the current kernel
- Installation may take 30-60 seconds
