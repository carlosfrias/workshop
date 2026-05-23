# domain-validation — Evidence Threshold Validation

## Purpose

Handles automated evidence validation at threshold levels for gemma4:e4b testing.

## Conventions

- **Evidence Sources:** Minimum 3 independent sources for Level 1
- **Threshold Levels:** Level 0 = single source, Level 1 = 3+, Level 2 = 5+, Level 3 = 10+
- **Validation Format:** Explicit source counts and level classification

## Mandatory Rules

1. No evidence can be marked valid below Level 1 without explicit justification
2. Count only truly independent sources
3. Every validation must explicitly state the threshold applied

## Prohibited

- No implicit validity without threshold check
- No partial source counts
- No hedging ("probably", "likely", "possibly")

## Documentation Protocol

Create entries in Activity Log.md with timestamp, item, source count, level, status, cross-references.
