---
name: signal-to-trade
description: Research a trading signal, then evaluate and size the position based on findings
steps:
  - agent: market-research
    task: |
      Research the following signal request and produce a structured signal report:

      {task}

      Include: instrument, direction, confidence level, backtest summary (with transaction costs), and data source citations.
    cwd: ./market-research
  - agent: position-management
    task: |
      Based on the following market research signal, evaluate and size the position:

      {previous}

      Check risk limits, determine position size using the defined methodology, and define exit criteria. Report the recommended trade parameters.
    cwd: ./position-management
---