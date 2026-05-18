# Sub-Task 21: Decision — Is Driver Fix Needed?

## Instruction

Analyze the results from all diagnostic sub-tasks and determine whether the r8168 driver fix should be applied. This is a **decision-making step** that requires reasoning over multiple inputs.

## Input

Results from previous sub-tasks:

```json
{
  "ping_gateway": {"success": true, "packet_loss_percent": 0},
  "ping_internet": {"success": false, "packet_loss_percent": 100},
  "dns_resolution": {"dns_works": false},
  "driver_info": {"driver_name": "r8169"},
  "r8169_loaded": true,
  "r8168_loaded": false,
  "tcpdump": {"packets_observed_leaving": true, "pattern": "outbound_only"},
  "firewall": {"firewall_blocking": false}
}
```

## Decision Logic

Apply the driver fix if **ALL 7** of the following conditions are true:

1. `ping_gateway.success == true` (LAN works)
2. `ping_internet.success == false` (internet fails)
3. `driver_info.driver_name == "r8169"` (buggy driver)
4. `r8169_loaded == true` (buggy driver is loaded)
5. `r8168_loaded == false` (correct driver is NOT loaded)
6. `tcpdump.packets_observed_leaving == true` AND `tcpdump.pattern == "outbound_only"` (packets leave but no replies)
7. `firewall.firewall_blocking == false` (firewall is not blocking)

## Expected Output Format

```json
{
  "task": "decision_driver_fix",
  "fix_recommended": true,
  "confidence": "high",
  "conditions_met": {
    "lan_works": true,
    "internet_fails": true,
    "r8169_driver": true,
    "r8169_loaded": true,
    "r8168_not_loaded": true,
    "packets_leaving_no_reply": true,
    "firewall_clear": true
  },
  "conditions_count": 7,
  "conditions_required": 7,
  "reasoning": [
    "Gateway ping succeeded (LAN functional)",
    "Internet ping failed (100% packet loss)",
    "r8169 driver is loaded (known buggy for RTL8168H)",
    "r8168 driver is not loaded",
    "tcpdump confirms packets leaving but no replies returning",
    "Firewall is not blocking traffic"
  ]
}
```

## Verification Criteria

- [ ] `fix_recommended` is boolean (true/false)
- [ ] `confidence` is one of: "high", "medium", "low", "very_low"
- [ ] `conditions_met` includes all 7 conditions as booleans
- [ ] `conditions_count` equals the number of true values in `conditions_met`
- [ ] `reasoning` has at least one item per true condition
- [ ] JSON is valid and parseable

## Confidence Levels

| Conditions Met | Confidence | Action |
|----------------|------------|--------|
| 7/7 | high | Apply fix immediately |
| 5-6/7 | medium | Apply fix, but investigate other causes if it doesn't work |
| 3-4/7 | low | Fix may help, but other issues likely present |
| 0-2/7 | very_low | Do NOT apply fix — investigate other causes first |

## Example: High Confidence (All Conditions Met)

```json
{
  "task": "decision_driver_fix",
  "fix_recommended": true,
  "confidence": "high",
  "conditions_met": {
    "lan_works": true,
    "internet_fails": true,
    "r8169_driver": true,
    "r8169_loaded": true,
    "r8168_not_loaded": true,
    "packets_leaving_no_reply": true,
    "firewall_clear": true
  },
  "conditions_count": 7,
  "conditions_required": 7,
  "reasoning": [
    "Gateway ping succeeded (LAN functional)",
    "Internet ping failed (100% packet loss)",
    "r8169 driver is loaded (known buggy for RTL8168H)",
    "r8168 driver is not loaded",
    "tcpdump confirms packets leaving but no replies returning",
    "Firewall is not blocking traffic"
  ]
}
```

## Example: Medium Confidence (Some Conditions Not Met)

```json
{
  "task": "decision_driver_fix",
  "fix_recommended": true,
  "confidence": "medium",
  "conditions_met": {
    "lan_works": true,
    "internet_fails": true,
    "r8169_driver": true,
    "r8169_loaded": true,
    "r8168_not_loaded": true,
    "packets_leaving_no_reply": null,
    "firewall_clear": true
  },
  "conditions_count": 5,
  "conditions_required": 7,
  "reasoning": [
    "Gateway ping succeeded (LAN functional)",
    "Internet ping failed (100% packet loss)",
    "r8169 driver is loaded",
    "r8168 driver is not loaded",
    "tcpdump not available (permission denied)",
    "Firewall is not blocking traffic"
  ]
}
```

## Notes

- This step requires **CLOUD model** execution (reasoning over multiple inputs)
- Do NOT execute the fix — just recommend it
- Pass this decision to Sub-Task 22 for execution if `fix_recommended == true`
