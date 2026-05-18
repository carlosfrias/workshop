#!/bin/bash
#
# project-blueprint-setup.sh
#
# Automated setup for AI-orchestrated projects using project-blueprint
#
# Usage:
#   ./project-blueprint-setup.sh <project-name> "<project-description>"
#   ./project-blueprint-setup.sh --interactive
#
# Example:
#   ./project-blueprint-setup.sh "healthcare-analytics" "Healthcare analytics with patient records, billing, and compliance"
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if pi is installed
    if ! command -v pi &> /dev/null; then
        print_error "pi is not installed. Please install pi first: https://github.com/mariozechner/pi-coding-agent"
        exit 1
    fi
    print_success "pi is installed: $(pi --version 2>&1 | head -1)"
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    print_success "Node.js is installed: $(node --version)"
    
    # Check if git is installed (optional)
    if command -v git &> /dev/null; then
        print_success "git is installed: $(git --version)"
    else
        echo -e "${YELLOW}⚠ git is not installed (optional, but recommended)${NC}"
    fi
}

interactive_mode() {
    print_header "Interactive Setup"
    
    echo "Let's set up your new AI-orchestrated project!"
    echo ""
    
    # Project name
    read -p "Project name (lowercase, no spaces): " PROJECT_NAME
    if [ -z "$PROJECT_NAME" ]; then
        print_error "Project name is required"
        exit 1
    fi
    
    # Project description
    read -p "Project description (1-2 sentences): " PROJECT_DESC
    if [ -z "$PROJECT_DESC" ]; then
        print_error "Project description is required"
        exit 1
    fi
    
    # Domains
    echo ""
    echo "Now let's add your domains. A domain is a major area of work."
    echo "Examples: bookkeeping, compliance, research, patient-records, billing, etc."
    echo ""
    
    DOMAINS=()
    DOMAIN_DESCS=()
    DOMAIN_KEYWORDS=()
    
    while true; do
        read -p "Domain name (lowercase, e.g., 'bookkeeping'): " domain_name
        if [ -z "$domain_name" ] && [ ${#DOMAINS[@]} -eq 0 ]; then
            print_error "At least one domain is required"
            continue
        elif [ -z "$domain_name" ]; then
            break
        fi
        
        read -p "Domain description (1 sentence): " domain_desc
        read -p "Keywords for routing (comma-separated, e.g., 'trades, reconciliation, P&L'): " domain_keywords
        
        DOMAINS+=("$domain_name")
        DOMAIN_DESCS+=("$domain_desc")
        DOMAIN_KEYWORDS+=("$domain_keywords")
        
        print_success "Added domain: $domain_name"
        echo ""
    done
    
    # Wiki location
    read -p "Wiki location (default: ./wiki/): " WIKI_LOCATION
    WIKI_LOCATION=${WIKI_LOCATION:-"./wiki/"}
    
    # HTML wiki
    read -p "Build HTML wiki with sidebar and search? (y/n, default: y): " html_wiki
    html_wiki=${html_wiki:-y}
    if [ "$html_wiki" = "y" ] || [ "$html_wiki" = "Y" ]; then
        HTML_WIKI="true"
    else
        HTML_WIKI="false"
    fi
    
    # Model preferences
    echo ""
    echo "Model configuration:"
    read -p "Orchestrator model (default: current pi default): " ORCH_MODEL
    read -p "Sub-agent model for reasoning tasks (default: anthropic/claude-sonnet-4): " SUB_MODEL
    SUB_MODEL=${SUB_MODEL:-"anthropic/claude-sonnet-4"}
    
    # Check-back behavior
    read -p "Should sub-agents check back via intercom? (y/n, default: y): " checkback
    checkback=${checkback:-y}
    if [ "$checkback" = "y" ] || [ "$checkback" = "Y" ]; then
        CHECKBACK="true"
    else
        CHECKBACK="false"
    fi
    
    # Create project directory
    PROJECT_DIR="$HOME/projects/$PROJECT_NAME"
    
    print_header "Configuration Summary"
    echo "Project Name:     $PROJECT_NAME"
    echo "Description:      $PROJECT_DESC"
    echo "Domains:          ${#DOMAINS[@]}"
    for i in "${!DOMAINS[@]}"; do
        echo "  - ${DOMAINS[$i]}: ${DOMAIN_KEYWORDS[$i]}"
    done
    echo "Wiki Location:    $WIKI_LOCATION"
    echo "HTML Wiki:        $HTML_WIKI"
    echo "Sub-agent Model:  $SUB_MODEL"
    echo "Intercom:         $CHECKBACK"
    echo "Project Dir:      $PROJECT_DIR"
    echo ""
    
    read -p "Proceed with setup? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_error "Setup cancelled"
        exit 1
    fi
}

create_project_directory() {
    print_header "Creating Project Directory"
    
    PROJECT_DIR="$HOME/projects/$PROJECT_NAME"
    
    if [ -d "$PROJECT_DIR" ]; then
        print_error "Directory already exists: $PROJECT_DIR"
        exit 1
    fi
    
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    print_success "Created: $PROJECT_DIR"
    
    # Initialize git
    if command -v git &> /dev/null; then
        git init
        print_success "Initialized git repository"
    fi
}

install_packages() {
    print_header "Installing Required Packages"
    
    print_step "Installing project-blueprint skill..."
    if pi install npm:project-blueprint; then
        print_success "project-blueprint installed"
    else
        print_error "Failed to install project-blueprint"
        echo "Trying GitHub source..."
        if pi install git:github.com/carlosfrias/project-blueprint; then
            print_success "project-blueprint installed from GitHub"
        else
            print_error "Failed to install project-blueprint from GitHub"
            exit 1
        fi
    fi
    
    print_step "Installing pi-subagents extension..."
    if pi install npm:pi-subagents; then
        print_success "pi-subagents installed"
    else
        print_error "Failed to install pi-subagents"
        exit 1
    fi
    
    print_step "Installing pi-intercom extension..."
    if pi install npm:pi-intercom; then
        print_success "pi-intercom installed"
    else
        print_error "Failed to install pi-intercom"
        exit 1
    fi
    
    print_step "Installing @yeliu84/pi-model-router extension..."
    if pi install npm:@yeliu84/pi-model-router; then
        print_success "@yeliu84/pi-model-router installed"
    else
        print_error "Failed to install @yeliu84/pi-model-router"
        exit 1
    fi
    
    print_step "Verifying installation..."
    pi list packages > /tmp/pi-packages.txt
    if grep -q "project-blueprint" /tmp/pi-packages.txt && \
       grep -q "pi-subagents" /tmp/pi-packages.txt && \
       grep -q "pi-intercom" /tmp/pi-packages.txt; then
        print_success "All packages verified"
    else
        print_error "Package verification failed"
        cat /tmp/pi-packages.txt
        exit 1
    fi
}

run_setup_wizard() {
    print_header "Running Setup Wizard"
    
    # Build the prompt
    DOMAIN_LIST=""
    for i in "${!DOMAINS[@]}"; do
        DOMAIN_LIST+="- ${DOMAINS[$i]} (${DOMAIN_DESCS[$i]}, keywords: ${DOMAIN_KEYWORDS[$i]})\n"
    done
    
    PROMPT="Set up a new project for $PROJECT_DESC

Domains:
$DOMAIN_LIST

Configuration:
- Wiki location: $WIKI_LOCATION
- HTML wiki: $HTML_WIKI
- Sub-agent model: $SUB_MODEL
- Intercom check-back: $CHECKBACK

Please create the complete project structure with agent definitions, chain files, and wiki documentation."

    echo "Running the setup wizard..."
    echo ""
    echo "This will take a few minutes as the agent creates files."
    echo "You can watch the progress in your pi session."
    echo ""
    
    # Run pi with the setup prompt
    # Note: This requires pi to support non-interactive mode
    # If pi doesn't support this, user will need to run manually
    if command -v pi &> /dev/null; then
        echo "$PROMPT" | pi
        print_success "Setup wizard completed"
    else
        print_error "pi command failed"
        echo ""
        echo "Please run this prompt manually in pi:"
        echo ""
        echo "$PROMPT"
    fi
}

verify_setup() {
    print_header "Verifying Setup"
    
    print_step "Checking project structure..."
    
    # Check root AGENTS.md
    if [ -f "AGENTS.md" ]; then
        print_success "AGENTS.md exists"
    else
        print_error "AGENTS.md not found"
    fi
    
    # Check .pi/APPEND_SYSTEM.md
    if [ -f ".pi/APPEND_SYSTEM.md" ]; then
        print_success ".pi/APPEND_SYSTEM.md exists"
    else
        print_error ".pi/APPEND_SYSTEM.md not found"
    fi
    
    # Check domain directories
    for domain in "${DOMAINS[@]}"; do
        if [ -d "$domain" ] && [ -f "$domain/AGENTS.md" ]; then
            print_success "Domain '$domain' exists with AGENTS.md"
        else
            print_error "Domain '$domain' not found or missing AGENTS.md"
        fi
    done
    
    # Check wiki
    if [ -d "wiki" ]; then
        print_success "Wiki directory exists"
    else
        print_error "Wiki directory not found"
    fi
    
    # Check .pi/agents/
    if [ -d ".pi/agents" ]; then
        agent_count=$(ls -1 .pi/agents/*.md 2>/dev/null | wc -l)
        print_success ".pi/agents/ exists with $agent_count agent definitions"
    else
        print_error ".pi/agents/ not found"
    fi
    
    # Token budget check
    echo ""
    print_step "Checking token budget..."
    if [ -f "AGENTS.md" ] && [ -f ".pi/APPEND_SYSTEM.md" ]; then
        root_size=$(wc -c < AGENTS.md)
        append_size=$(wc -c < .pi/APPEND_SYSTEM.md)
        total=$((root_size + append_size))
        echo "  Orchestrator permanent load: $total bytes (~$((total / 1024)) KB)"
        if [ $total -lt 2048 ]; then
            print_success "Token budget OK (< 2KB)"
        else
            print_error "Token budget too large (> 2KB)"
        fi
    fi
}

print_next_steps() {
    print_header "Setup Complete! Next Steps:"
    
    echo "1. Review the project structure:"
    echo "   cd $PROJECT_DIR"
    echo "   ls -la"
    echo ""
    
    echo "2. Read the routing table:"
    echo "   cat AGENTS.md"
    echo ""
    
    echo "3. Try a simple task:"
    echo "   pi \"<Your first task in one of the domains>\""
    echo ""
    
    echo "4. Read the wiki documentation:"
    echo "   cd wiki"
    echo "   cat */00\\ —\\ Home.md"
    echo ""
    
    echo "5. (Optional) Set up HTML wiki:"
    if [ "$HTML_WIKI" = "true" ]; then
        echo "   cd wiki-build"
        echo "   npm install"
        echo "   npm run dev"
    fi
    echo ""
    
    echo "Documentation:"
    echo "  - Quick Start: https://github.com/carlosfrias/trading-workspace/blob/main/technical-infrastructure/wiki/quick-start.md"
    echo "  - Project Blueprint: https://github.com/carlosfrias/project-blueprint"
    echo ""
    
    print_success "Happy orchestrating! 🚀"
}

# Main execution
main() {
    print_header "Project Blueprint Setup Script"
    
    # Parse arguments
    if [ "$1" = "--interactive" ] || [ "$1" = "-i" ]; then
        interactive_mode
    elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Usage: $0 <project-name> \"<project-description>\""
        echo "       $0 --interactive"
        echo ""
        echo "Examples:"
        echo "  $0 healthcare-analytics \"Healthcare analytics with patient records, billing, and compliance\""
        echo "  $0 trading-lab \"Trading laboratory with bookkeeping, position management, and research\""
        echo "  $0 -i  # Interactive mode"
        exit 0
    elif [ -n "$1" ] && [ -n "$2" ]; then
        PROJECT_NAME="$1"
        PROJECT_DESC="$2"
        
        # Default values for non-interactive mode
        DOMAINS=("domain1")
        DOMAIN_DESCS=("Default domain")
        DOMAIN_KEYWORDS=("default, keywords")
        WIKI_LOCATION="./wiki/"
        HTML_WIKI="true"
        SUB_MODEL="anthropic/claude-sonnet-4"
        CHECKBACK="true"
        
        echo "Using non-interactive mode with defaults."
        echo "For custom configuration, use: $0 --interactive"
        echo ""
    else
        print_error "Invalid arguments"
        echo "Usage: $0 <project-name> \"<project-description>\""
        echo "       $0 --interactive"
        echo "       $0 --help"
        exit 1
    fi
    
    # Run setup steps
    check_prerequisites
    create_project_directory
    install_packages
    run_setup_wizard
    verify_setup
    print_next_steps
}

# Run main function
main "$@"
