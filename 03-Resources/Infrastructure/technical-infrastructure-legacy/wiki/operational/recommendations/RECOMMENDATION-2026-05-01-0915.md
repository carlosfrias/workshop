# Recommendation: Consider ZFS for fnet1 Instead of LVM Next Time
**Date:** 2026-05-01 09:15  
**Context:** While rebuilding fnet1 storage with LVM. Noted that ZFS would give snapshots, compression, and self-healing.  
**Idea:** If fnet1 becomes a primary archive/backup target, ZFS datasets with `zfs snapshot` and `zfs send | receive` would be superior to LVM for data integrity.  
**Reference:** See BACKLOG.md TI-002 for current LVM rebuild. Revisit this recommendation if we add a 4th disk or if bit rot becomes a concern.
