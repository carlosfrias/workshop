---
name: decomposed-trade-to-log
description: Execute a trade and log it using decompose → execute → verify pattern (hybrid cloud/local)
steps:
  - agent: decomposer
    task: |
      Decompose the following trade execution and logging task into atomic sub-tasks:

      {task}

      Produce a structured decomposition plan with verification criteria for each sub-task.
      Route reasoning-heavy steps to cloud agents, structured steps to local agents.
    cwd: .
  - agent: position-management
    task: |
      Execute the following sub-task from the decomposition plan:

      {previous}

      Follow the expected output format specified in the plan. Include all required fields.
    cwd: ./position-management
  - agent: verifier
    task: |
      Verify the following output from position-management:

      Task: {task}
      Output: {previous}

      Apply the verification criteria from the decomposition plan.
      Produce a verification report with Pass/Fail/Partial recommendation.
    cwd: .
  - agent: bookkeeping
    task: |
      Log the following verified trade execution in the bookkeeping system:

      {previous}

      Only proceed if verification result is PASS or PARTIAL (with noted caveats).
      If verification failed, report the failure and do not log.
    cwd: ./bookkeeping
---