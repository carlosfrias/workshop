# Sub-Task 16: Analyze tcpdump Output

## Instruction

Analyze the raw tcpdump output from Sub-Task 15. Count outbound packets (source = local IP) and inbound packets (destination = local IP). Do NOT execute any commands — only parse the provided output.

## Input

- Raw tcpdump output from Sub-Task 15 (in `raw_output` field)
- Local IP address (optional, for more accurate counting)

## Parsing Rules

1. **Outbound packets**: Count lines containing `> 8.8.8.8` (or `> <external_ip>`)
2. **Inbound packets**: Count lines containing `8.8.8.8 >` (or `<external_ip> >`)
3. **Pattern**: 
   - `outbound_only` if outbound > 0 and inbound = 0
   - `bidirectional` if both outbound > 0 and inbound > 0
   - `none` if outbound = 0

## Expected Output Format

```json
{
  "task": "tcpdump_analyze",
  "outbound_count": 3,
  "inbound_count": 0,
  "pattern": "outbound_only",
  "packets_observed_leaving": true
}
```

## Verification Criteria

- [ ] `outbound_count` is a non-negative integer
- [ ] `inbound_count` is a non-negative integer
- [ ] `pattern` is one of: `"outbound_only"`, `"bidirectional"`, `"none"`
- [ ] `packets_observed_leaving` is boolean (true if outbound > 0)
- [ ] JSON is valid and parseable

## Example: Driver Issue Pattern (Outbound Only)

```json
{
  "task": "tcpdump_analyze",
  "outbound_count": 3,
  "inbound_count": 0,
  "pattern": "outbound_only",
  "packets_observed_leaving": true
}
```

**Interpretation:** Packets leave the interface but no replies return. Combined with r8169 driver, this indicates the driver produces malformed packets.

## Example: Normal Operation (Bidirectional)

```json
{
  "task": "tcpdump_analyze",
  "outbound_count": 3,
  "inbound_count": 3,
  "pattern": "bidirectional",
  "packets_observed_leaving": true
}
```

**Interpretation:** Network is functioning correctly at packet level.

## Example: No Packets

```json
{
  "task": "tcpdump_analyze",
  "outbound_count": 0,
  "inbound_count": 0,
  "pattern": "none",
  "packets_observed_leaving": false
}
```

**Interpretation:** No packets observed. Could be interface down, local firewall, or tcpdump permission issue.

## Notes

- Only parse — do NOT execute any commands
- Count lines, not individual packets (one line = one packet)
