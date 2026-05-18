# Recommendation: Examine Different Ansible Strategy for Model Pulls
**Date:** 2026-05-01 09:22  
**Context:** Currently Ollama models are pulled via `ollama pull` individually per node. During next session, investigate whether Ansible's `delegate_to` or parallel `async` polling could optimize model distribution from depot.  
**Idea:** Instead of each node pulling from internet (or even local depot sequentially), use Ansible to orchestrate parallel pulls with proper error handling and retry logic. Could also explore `ollama pull` via `ansible.builtin.command` with `async` and `poll` for non-blocking deployment across all nodes.  
**Reference:** Current `setup-ollama.yml` uses role-based sequential approach. Evaluate if `ansible.builtin.uri` to Ollama API or `async` task polling improves deployment speed.
