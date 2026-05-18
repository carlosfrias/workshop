#!/bin/bash
#
# ollama-setup.sh
#
# Automated Ollama installation and model configuration for pi
#
# Usage:
#   ./ollama-setup.sh
#   ./ollama-setup.sh --interactive
#   ./ollama-setup.sh --models gemma4:e4b,qwen3:8b,qwen3.5:4b
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
    print_success "Detected OS: $OS"
}

# Detect hardware
detect_hardware() {
    print_header "Detecting Hardware"
    
    if [[ "$OS" == "macos" ]]; then
        # macOS
        RAM_BYTES=$(sysctl -n hw.memsize)
        RAM_GB=$((RAM_BYTES / 1024 / 1024 / 1024))
        CPU=$(sysctl -n machdep.cpu.brand_string)
        
        echo "Total RAM: ${RAM_GB} GB"
        echo "CPU: $CPU"
        
        # Recommend models based on RAM
        if [ $RAM_GB -le 8 ]; then
            RECOMMENDED_MODELS=("qwen3.5:4b" "ministral-3:3b")
            MODEL_BUDGET=4
        elif [ $RAM_GB -le 16 ]; then
            RECOMMENDED_MODELS=("gemma4:e4b" "qwen3:8b" "qwen3.5:4b")
            MODEL_BUDGET=10
        elif [ $RAM_GB -le 24 ]; then
            RECOMMENDED_MODELS=("gemma4:e4b" "qwen3:14b" "qwen3:8b")
            MODEL_BUDGET=16
        else
            RECOMMENDED_MODELS=("gemma4:e4b" "qwen3:14b" "qwen3:8b" "codegemma:7b")
            MODEL_BUDGET=22
        fi
    else
        # Linux/Windows
        if command -v free &> /dev/null; then
            RAM_GB=$(free -g | awk '/^Mem:/ {print $2}')
        else
            RAM_GB=16  # Default assumption
        fi
        
        echo "Total RAM: ${RAM_GB} GB"
        
        # Same recommendations
        if [ $RAM_GB -le 8 ]; then
            RECOMMENDED_MODELS=("qwen3.5:4b" "ministral-3:3b")
            MODEL_BUDGET=4
        elif [ $RAM_GB -le 16 ]; then
            RECOMMENDED_MODELS=("gemma4:e4b" "qwen3:8b" "qwen3.5:4b")
            MODEL_BUDGET=10
        elif [ $RAM_GB -le 24 ]; then
            RECOMMENDED_MODELS=("gemma4:e4b" "qwen3:14b" "qwen3:8b")
            MODEL_BUDGET=16
        else
            RECOMMENDED_MODELS=("gemma4:e4b" "qwen3:14b" "qwen3:8b" "codegemma:7b")
            MODEL_BUDGET=22
        fi
    fi
    
    echo "Safe model budget: ${MODEL_BUDGET} GB (leaving 6 GB for OS)"
    echo "Recommended models: ${RECOMMENDED_MODELS[*]}"
}

# Install Ollama
install_ollama() {
    print_header "Installing Ollama"
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama is already installed: $(ollama --version)"
    else
        print_step "Installing Ollama..."
        
        if [[ "$OS" == "macos" ]] || [[ "$OS" == "linux" ]]; then
            curl -fsSL https://ollama.com/install.sh | sh
            print_success "Ollama installed"
        else
            print_error "Manual installation required for Windows"
            echo "Download from: https://ollama.com/download"
            exit 1
        fi
    fi
    
    # Start Ollama
    print_step "Starting Ollama service..."
    if [[ "$OS" == "macos" ]]; then
        # macOS runs as launchd service automatically
        print_success "Ollama service started (macOS launchd)"
    else
        # Linux - start in background
        ollama serve &
        sleep 3
        print_success "Ollama service started"
    fi
}

# Install local-model-pilot
install_local_model_pilot() {
    print_header "Installing local-model-pilot Skill"
    
    if ! command -v pi &> /dev/null; then
        print_error "pi is not installed. Please install pi first."
        exit 1
    fi
    
    print_step "Installing local-model-pilot skill..."
    if pi install npm:local-model-pilot 2>/dev/null; then
        print_success "local-model-pilot installed from npm"
    else
        print_step "Trying GitHub source..."
        if pi install git:github.com/carlosfrias/local-model-pilot 2>/dev/null; then
            print_success "local-model-pilot installed from GitHub"
        else
            print_error "Failed to install local-model-pilot"
            echo "Install manually: pi install git:github.com/carlosfrias/local-model-pilot"
        fi
    fi
}

# Pull models
pull_models() {
    print_header "Pulling Models"
    
    # Use command-line models if provided
    if [ -n "$CUSTOM_MODELS" ]; then
        IFS=',' read -ra MODELS <<< "$CUSTOM_MODELS"
        PULL_MODELS=("${MODELS[@]}")
    else
        PULL_MODELS=("${RECOMMENDED_MODELS[@]}")
    fi
    
    echo "Models to pull: ${PULL_MODELS[*]}"
    echo ""
    
    for model in "${PULL_MODELS[@]}"; do
        print_step "Pulling $model..."
        
        # Check if already installed
        if ollama list | grep -q "^$model "; then
            print_success "$model already installed"
        else
            ollama pull $model
            print_success "$model pulled"
        fi
    done
}

# Generate configuration
generate_config() {
    print_header "Generating Configuration"
    
    # Find local-model-pilot directory
    if [ -d "$HOME/.pi/agent/skills/local-model-pilot" ]; then
        LMP_DIR="$HOME/.pi/agent/skills/local-model-pilot"
    elif [ -d "./local-model-pilot" ]; then
        LMP_DIR="./local-model-pilot"
    else
        print_error "local-model-pilot directory not found"
        echo "Please run: pi install git:github.com/carlosfrias/local-model-pilot"
        return 1
    fi
    
    print_step "Scanning installed models..."
    cd "$LMP_DIR"
    ./scripts/scan-ollama-models.sh > /tmp/ollama-scan.json
    print_success "Model scan complete"
    
    print_step "Generating models.json and model-router.json..."
    echo ""
    echo "Configuration files should be generated at:"
    echo "  ~/.pi/agent/models.json"
    echo "  ~/.pi/agent/model-router.json"
    echo ""
    echo "Note: The actual config generation requires interaction with the agent."
    echo "Run this in pi:"
    echo ""
    echo "  cd $LMP_DIR"
    echo "  ./scripts/scan-ollama-models.sh"
    echo '  "Generate models.json and model-router.json based on my hardware"'
    echo ""
}

# Configure pi
configure_pi() {
    print_header "Configuring pi Settings"
    
    PI_SETTINGS="$HOME/.pi/agent/settings.json"
    
    if [ ! -f "$PI_SETTINGS" ]; then
        print_step "Creating settings.json..."
        mkdir -p "$HOME/.pi/agent"
        cat > "$PI_SETTINGS" << 'EOF'
{
  "defaultProvider": "router",
  "defaultModel": "auto",
  "packages": {
    "npm:@yeliu84/pi-model-router": "latest"
  }
}
EOF
        print_success "Created settings.json"
    else
        print_step "Updating settings.json..."
        
        # Check if router is configured
        if grep -q '"defaultProvider": "router"' "$PI_SETTINGS"; then
            print_success "model-router already configured"
        else
            # Backup and update
            cp "$PI_SETTINGS" "$PI_SETTINGS.bak"
            
            # Use jq if available, otherwise sed
            if command -v jq &> /dev/null; then
                jq '.defaultProvider = "router" | .defaultModel = "auto"' "$PI_SETTINGS" > /tmp/settings.json
                mv /tmp/settings.json "$PI_SETTINGS"
            else
                # Fallback to sed (basic replacement)
                print_step "Manual update recommended:"
                echo "Edit $PI_SETTINGS and add:"
                echo '  "defaultProvider": "router",'
                echo '  "defaultModel": "auto",'
            fi
        fi
    fi
    
    # Install pi-model-router
    print_step "Installing pi-model-router extension..."
    if pi install npm:@yeliu84/pi-model-router 2>/dev/null; then
        print_success "pi-model-router installed"
    else
        print_error "Failed to install pi-model-router"
        echo "Install manually: pi install npm:@yeliu84/pi-model-router"
    fi
}

# Validate setup
validate_setup() {
    print_header "Validating Setup"
    
    print_step "Checking Ollama..."
    if ollama list > /dev/null 2>&1; then
        model_count=$(ollama list | wc -l)
        print_success "Ollama running with $((model_count - 1)) models"
    else
        print_error "Ollama not responding"
    fi
    
    print_step "Checking pi configuration..."
    if [ -f "$HOME/.pi/agent/settings.json" ]; then
        if grep -q '"defaultProvider": "router"' "$HOME/.pi/agent/settings.json"; then
            print_success "model-router configured in settings.json"
        else
            print_error "model-router not configured"
        fi
    else
        print_error "settings.json not found"
    fi
    
    print_step "Checking models.json..."
    if [ -f "$HOME/.pi/agent/models.json" ]; then
        print_success "models.json exists"
    else
        print_error "models.json not found"
        echo "Generate with: cd local-model-pilot && ./scripts/scan-ollama-models.sh"
    fi
    
    print_step "Checking model-router.json..."
    if [ -f "$HOME/.pi/agent/model-router.json" ]; then
        print_success "model-router.json exists"
    else
        print_error "model-router.json not found"
        echo "Generate with local-model-pilot skill"
    fi
    
    # Run validation script if available
    if [ -d "$LMP_DIR" ] && [ -f "$LMP_DIR/scripts/validate-config.sh" ]; then
        print_step "Running configuration validation..."
        if $LMP_DIR/scripts/validate-config.sh 2>/dev/null; then
            print_success "Configuration validated"
        else
            print_error "Validation failed"
        fi
    fi
}

# Test setup
test_setup() {
    print_header "Testing Setup"
    
    echo "Run these tests in pi:"
    echo ""
    echo "1. Basic test (should route to fast model):"
    echo '   pi "What'\''s 2+2?"'
    echo ""
    echo "2. Reasoning test (should route to flagship model):"
    echo '   pi "Analyze the pros and cons of microservices"'
    echo ""
    echo "3. Check routing:"
    echo "   pi model-route"
    echo ""
}

# Print summary
print_summary() {
    print_header "Setup Complete!"
    
    echo "Ollama Installation:"
    echo "  Status: ✓ Complete"
    echo "  Models: ${PULL_MODELS[*]}"
    echo ""
    
    echo "pi Configuration:"
    echo "  Provider: router"
    echo "  Default Model: auto"
    echo "  Extensions: pi-model-router, local-model-pilot"
    echo ""
    
    echo "Next Steps:"
    echo "1. Generate configs (if not done automatically):"
    echo "   cd $LMP_DIR"
    echo "   ./scripts/scan-ollama-models.sh"
    echo '   "Generate models.json and model-router.json"'
    echo ""
    echo "2. Validate configuration:"
    echo "   ./scripts/validate-config.sh"
    echo ""
    echo "3. Test in pi:"
    echo '   pi "What'\''s 2+2?"'
    echo ""
    
    echo "Documentation:"
    echo "  - Ollama Setup Guide: technical-infrastructure/wiki/ollama-setup.md"
    echo "  - local-model-pilot: https://github.com/carlosfrias/local-model-pilot"
    echo "  - Quick Start: technical-infrastructure/wiki/quick-start.md"
    echo ""
    
    print_success "Happy orchestrating! 🚀"
}

# Interactive mode
interactive_mode() {
    print_header "Interactive Ollama Setup"
    
    echo "Let's configure Ollama for your system!"
    echo ""
    
    read -p "Custom models to pull (comma-separated, or press Enter for recommendations): " custom_models_input
    if [ -n "$custom_models_input" ]; then
        CUSTOM_MODELS="$custom_models_input"
    fi
    
    read -p "Install pi-model-router extension? (y/n, default: y): " install_router
    install_router=${install_router:-y}
    
    read -p "Generate configuration files automatically? (y/n, default: y): " generate_config_auto
    generate_config_auto=${generate_config_auto:-y}
}

# Main execution
main() {
    print_header "Ollama Setup Script"
    
    # Parse arguments
    if [ "$1" = "--interactive" ] || [ "$1" = "-i" ]; then
        interactive_mode
    elif [ "$1" = "--models" ] && [ -n "$2" ]; then
        CUSTOM_MODELS="$2"
    elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --interactive, -i     Interactive mode with prompts"
        echo "  --models <list>       Comma-separated list of models to pull"
        echo "  --help, -h            Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0"
        echo "  $0 --interactive"
        echo "  $0 --models gemma4:e4b,qwen3:8b,qwen3.5:4b"
        exit 0
    fi
    
    # Run setup steps
    detect_os
    detect_hardware
    install_ollama
    install_local_model_pilot
    pull_models
    generate_config
    configure_pi
    validate_setup
    test_setup
    print_summary
}

# Run main function
main "$@"
