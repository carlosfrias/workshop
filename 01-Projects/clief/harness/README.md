# Project Dependencies and Setup Instructions

## 💾 Local Setup
1.  **Clone:** `git clone <repo-url>`
2.  **Install:** `poetry install`
3.  **Run:** Depending on the task, initialize the process via:
    *   **Full Pipeline:** `harness/run_workflow.py --goal="[Your Goal]" --domain=all`
    *   **Design Review:** `harness/review_arch.py --domain=core-agent-architecture`

## 🧩 Model Configuration
| Component | Recommended Model | Fallback Model | Why? |
| :--- | :--- | :--- | :--- |
| **Orchestrator (Root)** | Anthropic Claude Opus | OpenAI GPT-4 | Best performance & planning capacity. |
| **Sub-Agent (Reasoning)** | Anthropic Claude Sonnet | Anthropic Claude Sonnet | Excellent complex reasoning and context handling. |
| **Sub-Agent (Fast Task)** | Anthropic Claude Haiku | N/A | Ideal for simple classification or data formatting. |

## 💪 Execution Flow Diagram (Conceptual)
1.  **Goal Input** (User) $\downarrow$
2.  **Router/Orchestrator** (`clief/AGENTS.md`) $\rightarrow$
3.  **Workflow Design** (Decomposition) $\rightarrow$
4.  **Core Agent Architecture** (Component Building) $\rightarrow$
5.  **Execution Simulation** $\rightarrow$
6.  **Evaluation Metrics** (Testing & Reporting) $\downarrow$
7.  **Final Result/Report** (User)