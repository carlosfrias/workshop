# Prompt Template: [S-TIGHT] Prompt Execution & Analysis Log

## Overview

*   **Date:** YYYY-MM-DD HH:MM:SS
*   **Issue Link:** [Link to the Issue Tracking document (ISSUE-TEMPLATE.md)]
*   **Session Link:** [Link to the entire session conversation log]
*   **Status Link:** [Link to the document updating the current status of the issue]

[S-TIGHT] **1. User Prompt (Verbatim)**
*   *The exact prompt provided by the user or the initiating agent.* 
    
```
[Paste the full, verbatim prompt used here.]
```

[S-TIGHT] **2. Outcome Section**
*   A comprehensive summary of the agent's immediate and intended output. This documents *what* was produced, not just *that* it was produced.
*   [Details of the output, including raw data, code blocks, or analyses.]

[S-TIGHT] **3. Decisions Made Section**
*   Document all critical forks in the path or operational decisions made during the session. Why were specific tools chosen? Why was an assumption made?
*   *Decision:* [Description of the decision] -> *Rationale:* [Why was this decision best?]

[S-TIGHT] **4. Files Changed Section**
*   If code or configuration files were modified, list them here.
*   *File Path:* [path/to/file.py] - *Change:* [A brief summary of the change, e.g., Added API wrapper for XYZ call.]

[S-TIGHT] **5. Lessons for Future Prompts (MANDATORY)**
*   What worked well? What was ambiguous? How can the prompt be improved to bypass identical issues next time? This section must prevent repeating mistakes.
*   *Improvement:* [Refine the wording, add constraints, or provide explicit negative examples.]

[S-TIGHT] **6. Follow-up Prompts & Next Steps**
*   List links to subsequent prompts/sessions that originated from this one, creating a traceable workflow path.
*   [Link to Follow-up Prompt 1]
*   [Link to Follow-up Prompt 2]

---
*Goal: To create an immutable, traceable record of every prompt execution, making the system's logic, decisions, and successes/failures explicit.*