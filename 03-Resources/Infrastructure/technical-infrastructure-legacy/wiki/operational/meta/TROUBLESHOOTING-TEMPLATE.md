# Troubleshooting Template: [S-TIGHT] Investigation & Resolution Activity Log

## Overview

*   **Problem Investigated:** [Clear, concise statement of the suspected malfunction or unexpected behavior.]
*   **Date Initiated:** YYYY-MM-DD HH:MM:SS
*   **Current Focus:** [What is the specific variable/component being tested or reviewed right now?]

[S-TIGHT] **1. Problem Statement**
*   A detailed description of the symptom observed, including timestamps, affected components (e.g., 'The trade execution system fails on orders > $1M'), and expected vs. actual behavior mismatch.

[S-TIGHT] **2. Hypotheses to Test**
*   *Generate a list of plausible root causes, ordered by likelihood.*
    
**Hypothesis A:** [e.g., The API key is expired.] — *Rationale:* [Why might this be true?]
**Hypothesis B:** [e.g., The background worker memory leak.] — *Rationale:* [Why might this be true?]
**Hypothesis C:** [e.g., Incorrect data serialization in the ETL stage.] — *Rationale:* [Why might this be true?]

[S-TIGHT] **3. Investigation Steps**
*   Document every single step taken to test a hypothesis or narrow down the error source. This section acts as a repeatable procedure log.
    
1. **Action:** [Executed `bash` command, or Checked file X, or Re-ran Job Y].
2. **Expected Outcome:** [What should have happened if the hypothesis was correct].
3. **Actual Result:** [What actually happened, e.g., "Command returned Error 401: Unauthorized"].
4. **Conclusion:** [Does this result support, refute, or are inconclusive regarding the hypothesis?]

[S-TIGHT] **4. Expected Evidence & Analysis**
*   What data points or logs were required to resolve this? Reference those logs directly.
*   **Key Log Snippet:** (Attach or paste relevant logs here)
*   **Analysis:** [Synthesize the evidence collected from Step 3 and explain the findings clearly.]

[S-TIGHT] **5. Related Links & Closure**
*   **Related Issues:** [Link to the associated ISSUE-TEMPLATE.md file.]
*   **Analysis/Resolution Files:** [Link to specific diagnostic or reproduction files (e.g., `debug-dump-20260514.json`).]
*   **Final Resolution:** [If solved, state the definitive root cause and the fix applied.]

---
*Goal: To methodically deconstruct complex faults, ensuring that the investigation process is repeatable, traceable, and directly links symptoms to verifiable root causes.*