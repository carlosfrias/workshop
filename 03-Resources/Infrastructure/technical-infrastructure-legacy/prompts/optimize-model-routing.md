# Model Routing Optimization Prompt

Use this prompt to refine or reset the model routing configuration for the Trading Desk. 

## Prompt Template

"Analyze the current model routing configuration across `.pi/model-router.json` and `~/.pi/agent/models.json`. 

**Objective:** Optimize the routing of tasks to models based on cognitive capacity (parameter count) and specific task requirements.

**Requirements:**
1. **High-Capacity Integration:** Identify and add high-capacity models (typically >290B parameters) from the provided cloud provider (e.g., `ollama`) into `models.json`.
2. **Tiered Routing:** Define three distinct reasoning tiers in `model-router.json`:
   - `ultra-reasoning`: Top-tier (1T+ params), high thinking, for mission-critical design.
   - `reasoning`: Mid-tier (600B+ params), medium thinking, for complex analysis.
   - `cloud-standard`: High-capacity (300B+ params), low thinking, for detailed drafting.
3. **Keyword Calibration:** Update the keyword lists for each route to ensure high-priority reasoning tasks are not routed to lightweight models.
4. **Schema Synchronization:** Ensure the model IDs in `model-router.json` match exactly the IDs defined in `models.json` and adhere to the strict schema required by the `pi-model-router` extension to avoid manual intervention.
5. **Documentation:** Generate or update a comprehensive `model-routing-guide.md` in the wiki detailing the routing tiers, triggers, and manual override scenarios.
6. **Global Promotion:** Ensure critical routing configs are promoted to the global `~/.pi/` directory for cross-session consistency.

**Verification:** Verify the final configuration by simulating common tasks (e.g., 'Analyze this risk' vs 'Log this trade') and confirming the expected model is selected."
