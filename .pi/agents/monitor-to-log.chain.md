---
name: monitor-to-log
description: Monitor positions and log status — fully local pipeline for routine checks
steps:
  - agent: position-monitor
    task: |
      Perform the following position monitoring task:

      {task}

      Report current position state, check risk limits, flag any violations. Do NOT execute any trades or submit orders.
    cwd: ./position-management
  - agent: bookkeeping
    task: |
      Log the following position status update in the bookkeeping system:

      {previous}

      Record all relevant position data, update running balance, and calculate unrealized P&L if applicable.
    cwd: ./bookkeeping
---