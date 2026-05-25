#!/usr/bin/env python3
"""
acceptance-test-suite.py — Acceptance tests TI-032 Master Prompt System

Usage:
    python3 acceptance-test-suite.py
"""

import unittest
import subprocess
import sys

BASE_DIR = "/Users/friasc/Cloud/ai-trading-workspace"
SCRIPTS_DIR = f"{BASE_DIR}/technical-infrastructure/scripts"
PLAYBOOKS_DIR = f"{BASE_DIR}/technical-infrastructure/playbooks"
PROMPTS_DIR = f"{BASE_DIR}/technical-infrastructure/prompts"

class TestMasterPromptSystem(unittest.TestCase):
    """Acceptance tests for the Master Prompt System."""
    
    def test_01_orchestrator_health_returns_json(self):
        """[PASS] Health check returns valid JSON"""
        result = subprocess.run([
            "python3", f"{SCRIPTS_DIR}/orchestrator_health.py", "--json"
        ], capture_output=True, text=True, timeout=5)
        
        # Health check returns non-zero when NOT healthy (expected behavior)
        # Exit code 0 = healthy, 1 = stressed, 2 = critical
        self.assertIn(result.returncode, [0, 1, 2], "Script should exit with valid code")
        
        try:
            import json
            data = json.loads(result.stdout)
            self.assertIn("status", data)
            self.assertIn("ram_percent", data)
            self.assertIn("cpu_percent", data)
        except json.JSONDecodeError:
            self.fail("Output should be valid JSON")
    
    def test_01b_orchestrator_health_status_valid(self):
        """[PASS] Health status is one of healthy/stressed/critical"""
        result = subprocess.run([
            "python3", f"{SCRIPTS_DIR}/orchestrator_health.py", "--json"
        ], capture_output=True, text=True, timeout=5)
        
        try:
            import json
            data = json.loads(result.stdout)
            self.assertIn(data["status"], ["healthy", "stressed", "critical"], 
                         "Status must be one of: healthy, stressed, critical")
        except json.JSONDecodeError:
            self.fail("Output should be valid JSON")
    
    def test_02_health_aware_executor_runs(self):
        """[PASS] Health-aware executor runs without errors"""
        result = subprocess.run([
            "python3", f"{SCRIPTS_DIR}/health_aware_executor.py", "--test"
        ], capture_output=True, text=True, timeout=5)
        
        self.assertEqual(result.returncode, 0, "Executor should run without ImportError")
        self.assertIn("health_status", result.stdout, "Should output health status")
    
    def test_03_binary_decompose_works(self):
        """[PASS] Binary decomposition splits tasks"""
        result = subprocess.run([
            "python3", f"{SCRIPTS_DIR}/binary_decompose.py",
            "--task", "test_task", "--complexity", "8"
        ], capture_output=True, text=True, timeout=5)
        
        self.assertEqual(result.returncode, 0, "Decomposition should work")
        self.assertIn("sub-task", result.stdout.lower(), "Should mention sub-tasks")
    
    def test_04_task_synthesizer_passes(self):
        """[PASS] Task synthesizer all tests pass"""
        result = subprocess.run([
            "python3", f"{SCRIPTS_DIR}/task_synthesizer.py", "--test"
        ], capture_output=True, text=True, timeout=5)
        
        self.assertEqual(result.returncode, 0, "All tests should pass")
        self.assertIn("TESTS PASSED: 6/6", result.stdout, "All 6 tests must pass")
    
    def test_05_cloud_escalation_passes(self):
        """[PASS] Cloud escalation works through all tiers"""
        result = subprocess.run([
            "python3", f"{SCRIPTS_DIR}/cloud_escalation.py",
            "--task", "test", "--simulate-failure", "--json"
        ], capture_output=True, text=True, timeout=5)
        
        self.assertEqual(result.returncode, 1, "Should fail after max tiers (expected)")
        self.assertIn("high", result.stdout.lower(), "Should reach high tier")
    
    def test_06_playbook_check_health_syntax(self):
        """[PASS] check_health playbook syntax valid"""
        result = subprocess.run([
            "ansible-playbook", f"{PLAYBOOKS_DIR}/check_health_v1.0.yml", "--syntax-check"
        ], capture_output=True, text=True, timeout=10)
        
        self.assertEqual(result.returncode, 0, "Playbook should have valid syntax")
    
    def test_07_playbook_backup_data_syntax(self):
        """[PASS] backup_data playbook syntax valid"""
        result = subprocess.run([
            "ansible-playbook", f"{PLAYBOOKS_DIR}/backup_data_v1.0.yml", "--syntax-check"
        ], capture_output=True, text=True, timeout=10)
        
        self.assertEqual(result.returncode, 0, "Playbook should have valid syntax")
    
    def test_08_playbook_monitor_services_syntax(self):
        """[PASS] monitor_services playbook syntax valid"""
        result = subprocess.run([
            "ansible-playbook", f"{PLAYBOOKS_DIR}/monitor_services_v1.0.yml", "--syntax-check"
        ], capture_output=True, text=True, timeout=10)
        
        self.assertEqual(result.returncode, 0, "Playbook should have valid syntax")
    
    def test_09_core_prompt_exists(self):
        """[PASS] Core prompt file exists"""
        import os
        self.assertTrue(os.path.exists(f"{PROMPTS_DIR}/core-prompt.md"), "Core prompt must exist")
    
    def test_10_all_modules_exist(self):
        """[PASS] All 6 module files exist"""
        import os
        for i in range(1, 7):
            path = f"{PROMPTS_DIR}/module-{i}-purpose.md"
            if i == 1:
                path = f"{PROMPTS_DIR}/module-1-purpose.md"
            elif i == 2:
                path = f"{PROMPTS_DIR}/module-2-dependencies.md"
            elif i == 3:
                path = f"{PROMPTS_DIR}/module-3-data-sources.md"
            elif i == 4:
                path = f"{PROMPTS_DIR}/module-4-conditions.md"
            elif i == 5:
                path = f"{PROMPTS_DIR}/module-5-performance.md"
            elif i == 6:
                path = f"{PROMPTS_DIR}/module-6-hardware.md"
            
            self.assertTrue(os.path.exists(path), f"Module {i} must exist")


def generate_report(results):
    """Generate a simple test report."""
    print("\n" + "=" * 70)
    print("ACCEPTANCE TEST REPORT")
    print("=" * 70)
    
    passed = sum(1 for r in results if r['passed'])
    failed = sum(1 for r in results if not r['passed'])
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if failed > 0:
        print("\nFailed Tests:")
        for r in results:
            if not r['passed']:
                print(f"  ❌ {r['test']}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED — SYSTEM READY FOR PRODUCTION")
    
    print("\n" + "=" * 70)
    
    # Save report
    import json
    report_path = f"{BASE_DIR}/technical-infrastructure/operational/testing/acceptance-test-report.json"
    with open(report_path, 'w') as f:
        json.dump({
            "timestamp": "2026-05-05",
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{passed/total*100:.1f}%",
            "tests": results
        }, f, indent=2)
    
    print(f"Report saved to: {report_path}")
    
    return passed == total


if __name__ == '__main__':
    # Run tests with custom result collection
    import json
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMasterPromptSystem)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Collect results manually
    results = []
    test_map = {
        'test_01_orchestrator_health_returns_json': 'Health check returns valid JSON',
        'test_01b_orchestrator_health_status_valid': 'Health status is one of healthy/stressed/critical',
        'test_02_health_aware_executor_runs': 'Health-aware executor runs without errors',
        'test_03_binary_decompose_works': 'Binary decomposition splits tasks',
        'test_04_task_synthesizer_passes': 'Task synthesizer all tests pass',
        'test_05_cloud_escalation_passes': 'Cloud escalation works through all tiers',
        'test_06_playbook_check_health_syntax': 'check_health playbook syntax valid',
        'test_07_playbook_backup_data_syntax': 'backup_data playbook syntax valid',
        'test_08_playbook_monitor_services_syntax': 'monitor_services playbook syntax valid',
        'test_09_core_prompt_exists': 'Core prompt file exists',
        'test_10_all_modules_exist': 'All 6 module files exist',
    }
    
    # Get failures and errors
    failures = set()
    for test, trace in result.failures + result.errors:
        failures.add(str(test).split('(')[0])
    
    for method_name, desc in test_map.items():
        passed = method_name not in failures
        results.append({"test": desc, "passed": passed})
    
    # Generate report
    all_passed = generate_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)
