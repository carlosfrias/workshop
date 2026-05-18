---
name: trade-to-log
description: Execute a position change, then log the trade in the bookkeeping system
steps:
  - agent: position-management
    task: |
      Execute the following position change request:

      {task}

      Verify API connectivity, check risk limits, and execute. Report fill details: instrument, side, quantity, fill price, timestamp, order type.
    cwd: ./position-management
  - agent: bookkeeping
    task: |
      Log the following trade execution in the bookkeeping system:

      {previous}

      Record the fill with all required fields, update running balance, and calculate realized P&L if applicable.
    cwd: ./bookkeeping
---