---
name: full-trade-cycle
description: Full pipeline from market research through position management to bookkeeping
steps:
  - agent: market-research
    task: |
      Research the following signal request and produce a structured signal report:

      {task}

      Include: instrument, direction, confidence level, backtest summary (with transaction costs), and data source citations.
    cwd: ./market-research
  - agent: position-management
    task: |
      Based on the following market research signal, evaluate, size, and execute the position:

      {previous}

      Check risk limits, determine position size, define exit criteria, and execute the trade. Report full fill details.
    cwd: ./position-management
  - agent: bookkeeping
    task: |
      Log the following trade execution in the bookkeeping system:

      {previous}

      Record the fill with all required fields, update running balance, and calculate realized P&L if applicable.
    cwd: ./bookkeeping
---