# Test Tier 9B + MLX — AGENTS

Testing qwen3.5:9b (GGUF), qwen3.5:9b-mlx (MLX), and gemma4:e4b-mlx (MLX) against the
same 3-concurrent-subagent DE benchmark used for previous model tests.

## Test Protocol

Each model runs the same 3-agent decompose-execute-verify test:
- 3 concurrent general-purpose subagents
- 300s timeout per agent
- Health monitoring at 60s intervals
- Same 3 claims/tasks as previous tests for consistency

### Models Under Test

| # | Model | Quant | Size | Context | Vision | Thinking | Tools |
|---|-------|-------|------|---------|--------|----------|-------|
| 1 | qwen3.5:9b | Q4_K_M | 6.6 GB | 262K | ✅ | ✅ | ✅ |
| 2 | qwen3.5:9b-mlx | nvfp4 | 8.9 GB | 262K | ✅ | ✅ | ✅ |
| 3 | gemma4:e4b-mlx | nvfp4 | 9.6 GB | 131K | ❌ | ✅ | ✅ |

### Risk Assessment

- Both 9b models have **262K context** — same as qwen3.5:4b which froze with maxTokens 16000
- maxTokens will be set **conservatively to 4096** for 9b models (262K ctx)
- gemma4:e4b-mlx has **131K context** — same as gemma4:e4b which passed all tests
- gemma4:e4b-mlx lacks vision — not a concern for DE text workloads