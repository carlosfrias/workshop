# TI-032 Master Prompt System Acceptance Testing

## Test Procedures

### 1. User Workflow: 'deploy app'
- Input: `deploy app`
- Expected: Execute `deploy_app_playbook`

### 2. User Workflow: 'what does X do'
- Input: `what does X do`
- Expected: Load `x_module`

### 3. Health Check Failure
- Simulate health failure
- Expected: Execution blocked with health check error

### 4. Unknown Keyword
- Input: `random keyword`
- Expected: Error with keyword suggestions

### 5. Complex Task Decomposition
- Input: `analyze system`
- Expected: Decompose into subtasks

### 6. Stressed System Escalation
- Simulate system stress
- Expected: Escalate to cloud resources

### 7. Empty Prompt
- Input: `"
- Expected: Error with usage hint

### 8. Multiple Keywords Matched
- Input: `backup database`
- Expected: Select best match `backup_database_playbook`

## Expected Results

| Test | Expected Outcome |
|------|------------------|
| deploy app | Execute playbook |
| what does X do | Load module |
| Health failure | Execution blocked |
| Unknown keyword | Error + suggestions |
| Complex task | Decomposed subtasks |
| Stressed system | Cloud escalation |
| Empty prompt | Usage hint |
| Multiple keywords | Best match selected |

## Troubleshooting

- **Test failure**: Check input formatting and system logs
- **Missing module**: Verify module installation
- **Timeout**: Increase test timeout or optimize workflow
- **Incorrect output**: Review playbook/module implementation

## Extending the Test Suite

1. Add new test methods to `acceptance-test-suite.py`
2. Update wiki documentation with new test procedures
3. Regenerate report with updated tests

Example extension:
```python
def test_new_feature(self):
    self.run_test("New test description", ["python", "master-prompt.py", "new command"], "Expected output")
```

Add to wiki:
### New Test: 'new command'
- Input: `new command`
- Expected: "Expected output"
"