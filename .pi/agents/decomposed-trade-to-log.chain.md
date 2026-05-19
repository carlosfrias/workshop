---
name: decomposed-trade-to-log
description: Execute a trade and log it using decompose → fleet-dispatch → verify → log pattern with three-tier cascade (fleet → intercom → subagent)
steps:
  - agent: decomposer
    task: |
      Decompose the following trade execution and logging task into atomic sub-tasks:

      {task}

      Produce a structured decomposition plan with verification criteria for each sub-task.
      Target Agent labels are capability labels (not dispatch addresses).
      The fleet-dispatcher will route each sub-task through the best available tier.
      Route reasoning-heavy steps to cloud agents, structured steps to local agents.
    cwd: .
  - agent: fleet-dispatcher
    task: |
      Route the following decomposition plan through the three-tier cascade (fleet → intercom → subagent):

      {previous}

      For each sub-task:
      1. Check fleet availability via coms_net_list()
      2. If fleet available, dispatch to fleet node (Tier 1)
      3. If no fleet, check intercom sessions (Tier 2)
      4. If no intercom, use subagent (Tier 3)
      5. Collect all results regardless of tier
      6. Produce Fleet-Dispatch Results with tier summary and sub-task results
    cwd: .
  - agent: verifier
    task: |
      Verify the following fleet-dispatch results against the original decomposition criteria:

      Task: {task}
      Output: {previous}

      Validate each sub-task result regardless of which tier executed it.
      Produce a verification report with Pass/Fail/Partial recommendation.
    cwd: .
  - agent: bookkeeping
    task: |
      Log the following verified trade execution in the bookkeeping system:

      {previous}

      Only proceed if verification result is PASS or PARTIAL (with noted caveats).
      If verification failed, report the failure and do not log.
    cwd: ./bookkeeping