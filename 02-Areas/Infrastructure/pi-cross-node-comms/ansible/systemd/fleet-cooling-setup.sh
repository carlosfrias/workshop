#!/bin/bash
# fleet-cooling-setup.sh — Apply runtime sysfs settings that don't persist across reboot
#
# Fan cooling: Intel NUCs have a Linux ACPI bug where fan cooling devices
# default to cur_state=0 (off) regardless of temperature. This forces them to max.
#
# CPU governor: Fleet nodes must use powersave to avoid unnecessary power/heat.
# fnet7 in particular resets to "performance" on reboot.
#
# Run via fleet-cooling.service (systemd oneshot) on every boot.

set -euo pipefail

echo "[fleet-cooling] Setting fan cooling devices to max..."
fan_count=0
for cd in /sys/class/thermal/cooling_device*; do
    type=$(cat "$cd/type" 2>/dev/null || true)
    if [ "$type" = "Fan" ]; then
        max_state=$(cat "$cd/max_state" 2>/dev/null || echo "1")
        echo "$max_state" | sudo tee "$cd/cur_state" > /dev/null
        fan_count=$((fan_count + 1))
    fi
done
echo "[fleet-cooling] Set $fan_count fan device(s) to max"

echo "[fleet-cooling] Setting CPU governor to powersave..."
echo "powersave" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
actual=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)
echo "[fleet-cooling] Governor: $actual"

echo "[fleet-cooling] Done"