---
name: decomposed-monitor-to-log
description: Monitor positions and log status using decompose → execute → verify pattern (fully local execution)
steps:
  - agent: decomposer
    task: |
      Decompose the following position monitoring and logging task into atomic sub-tasks:

      {task}

      Produce a structured decomposition plan with verification criteria for each sub-task.
      Target local model execution where possible.
    cwd: .
  - agent: position-monitor
    task: |
      Execute the following sub-task from the decomposition plan:

      {previous}

      Follow the expected output format specified in the plan. Be precise and complete.
    cwd: ./position-management
  - agent: verifier
    task: |
      Verify the following output from position-monitor:

      Task: {task}
      Output: {previous}

      Apply the verification criteria from the decomposition plan.
      Produce a verification report with Pass/Fail/Partial recommendation.
    cwd: .
  - agent: bookkeeping
    task: |
      Log the following verified position status in the bookkeeping system:

      {previous}

      Only proceed if verification result is PASS or PARTIAL (with noted caveats).
      If verification failed, report the failure and do not log.
    cwd: ./bookkeeping
---