#!/usr/bin/env python3
"""
Orchestration Framework Status Monitor

Monitors playbook execution, background scheduling, and decomposed script orchestration.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def check_playbooks():
    """Check playbook execution status"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Playbook Execution Status ==={Colors.END}\n")
    
    playbook_dir = Path("technical-infrastructure/playbooks")
    template_file = Path("technical-infrastructure/ansible-playbook-template.yml")
    
    if template_file.exists():
        print(f"{Colors.GREEN}✓{Colors.END} Playbook template: {template_file}")
    else:
        print(f"{Colors.RED}✗{Colors.END} Playbook template missing: {template_file}")
    
    if playbook_dir.exists():
        playbooks = list(playbook_dir.glob("*.yml"))
        print(f"{Colors.GREEN}✓{Colors.END} Playbook directory: {len(playbooks)} playbooks found")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} Playbook directory not found: {playbook_dir}")
    
    # Check wiki documentation
    wiki_file = Path("technical-infrastructure/wiki-playbook-structure.md")
    if wiki_file.exists():
        print(f"{Colors.GREEN}✓{Colors.END} Wiki structure: {wiki_file}")
    else:
        print(f"{Colors.RED}✗{Colors.END} Wiki structure missing: {wiki_file}")

def check_schedule():
    """Check background scheduler status"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Background Scheduler Status ==={Colors.END}\n")
    
    schedule_file = Path("technical-infrastructure/orchestration/schedules.yml")
    if schedule_file.exists():
        print(f"{Colors.GREEN}✓{Colors.END} Schedule configuration: {schedule_file}")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} Schedule configuration not found: {schedule_file}")
        print(f"   Creating default schedule...")
        
        # Create default schedule
        schedule_file.parent.mkdir(parents=True, exist_ok=True)
        schedule_content = """# Orchestration Schedules
# Auto-created by orchestrator-status.py

schedules:
  - name: "Daily playbook documentation update"
    schedule: "0 3 * * *"
    script: "scripts/update-playbook-wiki.sh"
    priority: low
    background: true
    
  - name: "Hourly status refresh"
    schedule: "0 * * * *"
    script: "scripts/refresh-status.py"
    priority: medium
    background: true
    
  - name: "Weekly performance report"
    schedule: "0 0 * * 0"
    script: "scripts/generate-weekly-report.py"
    priority: low
    background: true
"""
        schedule_file.write_text(schedule_content)
        print(f"{Colors.GREEN}✓{Colors.END} Default schedule created")

def check_queue():
    """Check decomposed script queue"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Decomposed Script Queue ==={Colors.END}\n")
    
    scripts_dir = Path("technical-infrastructure/scripts")
    if scripts_dir.exists():
        scripts = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh"))
        print(f"{Colors.GREEN}✓{Colors.END} Scripts directory: {len(scripts)} scripts found")
        
        # Show recent scripts
        if scripts:
            print(f"\n{Colors.BOLD}Recent Scripts:{Colors.END}")
            for script in sorted(scripts)[-5:]:
                print(f"  - {script.name}")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} Scripts directory not found: {scripts_dir}")

def check_triggers():
    """Check keyword router triggers"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Keyword Router Triggers ==={Colors.END}\n")
    
    trigger_file = Path("technical-infrastructure/ansible/group_vars/trigger_keywords.yml")
    if trigger_file.exists():
        print(f"{Colors.GREEN}✓{Colors.END} Trigger keywords: {trigger_file}")
        # Count triggers (simple line count for now)
        content = trigger_file.read_text()
        trigger_count = len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')])
        print(f"   {trigger_count} triggers registered")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} Trigger keywords not found: {trigger_file}")
        print(f"   Creating default triggers...")
        
        # Create default triggers
        trigger_file.parent.mkdir(parents=True, exist_ok=True)
        trigger_content = """# Trigger Keywords for Playbook Execution
# Format: keyword: playbook_file

# Deployment
deploy: deploy_app.yml
deploy_app: deploy_app.yml
update: update_packages.yml
update_packages: update_packages.yml

# Monitoring
health: check_health.yml
check_health: check_health.yml
monitor: monitor_services.yml
monitor_services: monitor_services.yml

# Maintenance
cleanup: cleanup_logs.yml
cleanup_logs: cleanup_logs.yml
backup: backup_data.yml
backup_data: backup_data.yml
"""
        trigger_file.write_text(trigger_content)
        print(f"{Colors.GREEN}✓{Colors.END} Default triggers created")

def test_keyword_match(test_phrase):
    """Test keyword matching"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Keyword Match Test ==={Colors.END}\n")
    print(f"Testing phrase: '{test_phrase}'")
    
    trigger_file = Path("technical-infrastructure/ansible/group_vars/trigger_keywords.yml")
    if not trigger_file.exists():
        print(f"{Colors.RED}✗{Colors.END} Trigger file not found. Run --triggers first.")
        return
    
    content = trigger_file.read_text().lower()
    test_phrase_lower = test_phrase.lower()
    
    # Simple keyword matching
    matches = []
    for line in content.split('\n'):
        if line.strip() and not line.strip().startswith('#'):
            if ':' in line:
                keyword = line.split(':')[0].strip()
                if keyword in test_phrase_lower:
                    matches.append(keyword)
    
    if matches:
        print(f"{Colors.GREEN}✓{Colors.END} Matched keywords: {', '.join(matches)}")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} No matching keywords found")

def health_check():
    """Full system health check"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}╔════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║  Orchestration Framework Health Check  ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚════════════════════════════════════════╝{Colors.END}\n")
    
    checks = {
        "Playbook Template": Path("technical-infrastructure/ansible-playbook-template.yml").exists(),
        "Wiki Structure": Path("technical-infrastructure/wiki-playbook-structure.md").exists(),
        "Low-Capacity Validation": Path("technical-infrastructure/wiki/technical-infrastructure/low-capacity-model-validation.md").exists(),
        "Status Monitor": Path("technical-infrastructure/wiki/technical-infrastructure/orchestration-status-monitor.md").exists(),
        "Trigger Keywords": Path("technical-infrastructure/ansible/group_vars/trigger_keywords.yml").exists(),
        "Schedule Config": Path("technical-infrastructure/orchestration/schedules.yml").exists(),
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {check_name}")
        if not passed:
            all_passed = False
    
    print(f"\n{'═' * 40}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}Overall Status: HEALTHY ✓{Colors.END}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}Overall Status: DEGRADED ⚠{Colors.END}")
        print(f"\n{Colors.YELLOW}Some components need attention.{Colors.END}")
    
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    parser = argparse.ArgumentParser(description="Orchestration Framework Status Monitor")
    parser.add_argument("--playbooks", action="store_true", help="Check playbook execution status")
    parser.add_argument("--schedule", action="store_true", help="Check background scheduler")
    parser.add_argument("--queue", action="store_true", help="Check decomposed script queue")
    parser.add_argument("--triggers", action="store_true", help="Check keyword router triggers")
    parser.add_argument("--test", type=str, help="Test keyword matching for a phrase")
    parser.add_argument("--health", action="store_true", help="Full system health check")
    
    args = parser.parse_args()
    
    if not any([args.playbooks, args.schedule, args.queue, args.triggers, args.test, args.health]):
        parser.print_help()
        sys.exit(0)
    
    if args.playbooks:
        check_playbooks()
    if args.schedule:
        check_schedule()
    if args.queue:
        check_queue()
    if args.triggers:
        check_triggers()
    if args.test:
        test_keyword_match(args.test)
    if args.health:
        health_check()

if __name__ == "__main__":
    main()
