---
name: {chain_name}
description: {chain_description}
steps:
  - agent: {agent1_name}
    task: |
      {agent1_task_template}
    cwd: ./{domain1}
  - agent: {agent2_name}
    task: |
      {agent2_task_template}
    cwd: ./{domain2}
---