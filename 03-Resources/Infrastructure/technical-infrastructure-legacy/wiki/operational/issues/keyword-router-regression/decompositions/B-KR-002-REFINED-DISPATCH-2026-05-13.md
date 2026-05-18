# B-KR-002 Refinement Dispatch — Fixed Regression Test + Narrowed Bisection

**Date:** 2026-05-13  
**Backlog Item:** B-KR-002  
**Status:** Wave 1 partial complete — test design flaw identified, bisection range narrowed  
**Next Action:** Fix regression test, re-run on narrowed range, then pivot if clean

---

## Refined Bisection Range

**Known GOOD:** 321b053 (`feat: P0 dispatch`)  
**Known BAD:** 4bce629 (`fix: prioritize keyword inference`)  
**Commits to test:** 4bce629, 5a0f7f1, 9186ab4, 93e1d39  

**Note:** 5445758 (HEAD) and 6ec16a5 are outside the narrowed range (one is post-kill-switch, one is pre- any code changes).

---

## Step 1: Fix Regression Test (fnet3, 5 min)

```typescript
intercom({
  action: "ask",
  to: "fnet3",
  message: `B-KR-002 Step 1: Fix the regression test.

The current test at test/bisect/regression-test.ts has a false positive: it checks for kill-switch config.enabled, which was added in B-KR-001 and does not exist in the bisection range commits.

Create a NEW test file: test/bisect/regression-test-v2.ts

Requirements:
- The test ONLY checks model selection for a reasoning prompt.
- It does NOT check kill-switch, config.enabled, or any B-KR-001 features.
- Input prompt: "analyze risk for NVDA" (a reasoning/complex prompt).
- Expected behavior: the selected model should be gemma4:e4b (medium-local) or higher tier (qwen3:8b, deepseek-v4-pro, kimi-k2.6).
- It should NOT select qwen3.5:4b (low-local) for this prompt.
- The test must be deterministic and runnable with: npm test -- test/bisect/regression-test-v2.ts

After writing the test:
1. Run it on commit 321b053 (known GOOD). It should PASS.
2. Run it on commit 5445758 (HEAD). It should PASS (we know model selection works here).
3. Report the test code and both test results.

Save the test file and report back.`
})
```

**Expected result:** fnet3 replies with the fixed test code and confirmation it passes on both GOOD and HEAD.

---

## Step 2: Re-Run Narrowed Bisection (Parallel, 15 min)

After Step 1 is confirmed, dispatch these simultaneously:

```typescript
// Commit 4bce629 (earliest in narrowed range — closest to GOOD)
intercom({
  action: "ask",
  to: "fnet1",
  message: `B-KR-002 Step 2: Re-run bisection on narrowed range.

1. git checkout 4bce629
2. Run: npm test -- test/bisect/regression-test-v2.ts
3. Report: PASS (model escalates to gemma4:e4b+) or FAIL (model stays at qwen3.5:4b)

This commit is: 4bce629 — fix(classifier): prioritize keyword inference over auto-complexity heuristic`
})

// Commit 5a0f7f1
intercom({
  action: "ask",
  to: "fnet2",
  message: `B-KR-002 Step 2: Re-run bisection on narrowed range.

1. git checkout 5a0f7f1
2. Run: npm test -- test/bisect/regression-test-v2.ts
3. Report: PASS or FAIL

This commit is: 5a0f7f1 — fix(TI-035): word-boundary matching`
})

// Commit 9186ab4
intercom({
  action: "ask",
  to: "fnet4",
  message: `B-KR-002 Step 2: Re-run bisection on narrowed range.

1. git checkout 9186ab4
2. Run: npm test -- test/bisect/regression-test-v2.ts
3. Report: PASS or FAIL

This commit is: 9186ab4 — feat: add /list-routes command`
})

// Commit 93e1d39
intercom({
  action: "ask",
  to: "fnet5",
  message: `B-KR-002 Step 2: Re-run bisection on narrowed range.

1. git checkout 93e1d39
2. Run: npm test -- test/bisect/regression-test-v2.ts
3. Report: PASS or FAIL

This commit is: 93e1d39 — fix: default route now delegates to model-router`
})
```

**Narrowed Range Progress Tracker:**
- [ ] fnet1: 4bce629 — Waiting
- [ ] fnet2: 5a0f7f1 — Waiting
- [ ] fnet3: Test fix + validation — Waiting
- [ ] fnet4: 9186ab4 — Waiting
- [ ] fnet5: 93e1d39 — Waiting

---

## Step 3: Pivot Decision Gate

After all replies come in, evaluate:

**If ANY commit shows FAIL (qwen3.5:4b selected):**
- That commit is the regression point (or near it).
- Dispatch Wave 2 (ROOT-001/002/003) to fnet3 to analyze that specific commit.

**If ALL commits show PASS (gemma4:e4b+ selected):**
- `pi-keyword-router` model selection is clean across entire history.
- The user's symptom ("always gets qwen3.5:4b") is caused by **something outside this package**.
- **Pivot to investigating:**
  1. `routing-transparency` package — does it override the selected model?
  2. Orchestrator config (`model-router.json`, `models.json`) — does it force low-tier?
  3. The actual pi session behavior — is the keyword-router even being invoked?

---

## Step 4a (if pivot needed): Investigate routing-transparency

```typescript
intercom({
  action: "ask",
  to: "fnet3",
  message: `B-KR-002 Pivot: Investigate routing-transparency.

The pi-keyword-router bisection shows model selection is correct in all commits. The regression must be elsewhere.

Check the routing-transparency package:
1. git log --oneline --all -- routing-transparency/
2. Look for commits that mention: 'model', 'tier', 'escalation', 'keyword', 'override', 'footer', 'qwen3.5:4b', 'default'.
3. Report any suspicious commits.
4. Check if routing-transparency/src/index.ts or src/footer.ts has logic that overrides or hides the model selected by keyword-router.
5. Specifically look for: does the footer display the model that keyword-router chose, or does it display a different model?

Report all findings.`
})
```

## Step 4b (if pivot needed): Investigate orchestrator config

```typescript
intercom({
  action: "ask",
  to: "fnet6",
  message: `B-KR-002 Pivot: Investigate orchestrator config.

The pi-keyword-router model selection is correct in all tested commits. The user reports they always get qwen3.5:4b on the orchestrator (Mac).

Check the orchestrator's config files:
1. Look for any .json config files in the workspace root or .pi/ directory that mention model selection.
2. Check if there is a model-router.json or models.json that forces a default model.
3. Check if there are environment variables or shell aliases that override model selection.
4. Report any config that could force qwen3.5:4b regardless of keyword-router's choice.

Note: You cannot access the Mac directly — report what you can infer from the repository or ask for remote data.`
})
```

---

## Ready to Execute

**Step 1** (fnet3) runs first. Upon confirmation, **Step 2** (fnet1, fnet2, fnet4, fnet5) fires in parallel.

**Dispatch Step 1 now:**
```typescript
intercom({ action: "ask", to: "fnet3", message: "B-KR-002 Step 1: Fix regression test..." })
```

**Estimated total time:** 20 minutes (5 min test fix + 15 min parallel bisection re-run).
