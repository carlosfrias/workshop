#!/bin/bash
# Pi Lab Nodes Validation Script
# Runs the complete validation workflow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$ANSIBLE_DIR/reports"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

cd "$ANSIBLE_DIR"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     PI LAB NODES VALIDATION                              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Step 1: Initial Test
echo "📋 Step 1: Testing current pi installation..."
ansible-playbook playbooks/test-pi-installation.yml -i inventory.yml || true

# Step 2: Install/Update Pi
echo ""
echo "📦 Step 2: Installing/Updating pi on all nodes..."
ansible-playbook playbooks/install-pi.yml -i inventory.yml || true

# Step 3: Run pi update
echo ""
echo "🔄 Step 3: Running 'pi update' on all nodes..."
ansible-playbook playbooks/update-pi.yml -i inventory.yml || true

# Step 4: Fix PATH issues
echo ""
echo "🔧 Step 4: Fixing PATH configuration..."
ansible-playbook playbooks/fix-pi-availability.yml -i inventory.yml || true

# Step 5: Reboot persistence test
echo ""
echo "🔄 Step 5: Testing reboot persistence (this will take 10-15 minutes)..."
read -p "Ready to reboot all nodes? Press Enter to continue or Ctrl+C to skip..."
ansible-playbook playbooks/test-reboot-persistence.yml -i inventory.yml || true

# Step 6: Final verification
echo ""
echo "✅ Step 6: Final verification..."
ansible-playbook playbooks/test-pi-installation.yml -i inventory.yml

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     VALIDATION COMPLETE                                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Reports saved to: $REPORTS_DIR"
