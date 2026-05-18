#!/bin/bash
# benchmark-model.sh - Test local model capacity for optimal model selection
# Tests: CPU, RAM, disk I/O, and Ollama model performance

set -e

echo "=== MODEL CAPACITY BENCHMARK REPORT ==="
echo "Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

echo "## SYSTEM RESOURCES"
echo ""

# CPU info
echo "### CPU"
echo "Cores: $(nproc)"
echo "Model: $(lscpu | grep "Model name" | cut -d: -f2 | xargs)"
lscpu | grep -E "^CPU\(s\)|^Thread|Core|Socket" | head -4
echo ""

# RAM info
echo "### RAM"
free -h | grep -E "Mem|Swap"
echo ""

# Disk info
echo "### Disk Space (Home Directory)"
df -h ~ | tail -1
echo ""

# Disk I/O test
echo "### Disk I/O Test (100MB write)"
dd if=/dev/zero of=~/benchmark-test.tmp bs=1M count=100 conv=fdatasync 2>&1 | tail -1
rm -f ~/benchmark-test.tmp
echo ""

echo "## OLLAMA STATUS"
echo ""

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "✓ Ollama is running"
    echo ""
    echo "### Available Models"
    ollama list 2>/dev/null || echo "No models pulled yet"
    echo ""
else
    echo "✗ Ollama is not running"
    echo "Start it with: ollama serve &"
    echo ""
fi

echo "## MODEL PERFORMANCE TESTS"
echo ""

# Test function for a model
test_model() {
    local model=$1
    local prompt="Count from 1 to 50. Only output numbers, one per line."
    
    echo "### Testing: $model"
    
    # Check if model exists
    if ! ollama list 2>/dev/null | grep -q "$model"; then
        echo "  Status: Not installed"
        echo "  Action: Run 'ollama pull $model'"
        echo ""
        return
    fi
    
    # Run benchmark
    echo "  Prompt: Simple counting task"
    start_time=$(date +%s.%N)
    
    output=$(ollama run $model "$prompt" 2>&1)
    end_time=$(date +%s.%N)
    
    duration=$(echo "$end_time - $start_time" | bc)
    tokens=$(echo "$output" | wc -w)
    speed=$(echo "scale=2; $tokens / $duration" | bc 2>/dev/null || echo "N/A")
    
    echo "  Duration: ${duration}s"
    echo "  Tokens: ~$tokens"
    echo "  Speed: ~${speed} tokens/sec"
    
    # Quality check (did it count correctly?)
    if echo "$output" | grep -q "49" && echo "$output" | grep -q "50"; then
        echo "  Quality: ✓ Pass (counted to 50)"
    else
        echo "  Quality: ⚠ Partial (may have truncated)"
    fi
    echo ""
}

# Check if Ollama is available
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "Skipping model tests - Ollama not running"
    echo ""
    echo "RECOMMENDATION: Start Ollama first:"
    echo "  ollama serve &"
    echo ""
else
    # Test common models (will skip if not installed)
    echo "Testing installed models..."
    echo ""
    
    test_model "gemma4:e4b"
    test_model "qwen3.5:4b"
    test_model "qwen3:8b"
    test_model "llama3.2:3b"
    test_model "phi3:3.8b"
fi

echo "## RECOMMENDATIONS"
echo ""

# Simple heuristic based on RAM
ram_gb=$(free -g | grep Mem | awk '{print $2}')

if [ "$ram_gb" -ge 16 ]; then
    echo "✓ System has ${ram_gb}GB RAM - can run 8B parameter models"
    echo "  Recommended: qwen3:8b or gemma4:e4b"
elif [ "$ram_gb" -ge 8 ]; then
    echo "✓ System has ${ram_gb}GB RAM - can run 4B-8B parameter models"
    echo "  Recommended: qwen3.5:4b or gemma4:e4b"
else
    echo "⚠ System has ${ram_gb}GB RAM - limited to small models"
    echo "  Recommended: llama3.2:3b or phi3:3.8b"
fi
echo ""

echo "## END OF BENCHMARK REPORT ==="
echo ""
echo "INSTRUCTIONS: Copy this entire report and paste it to the cloud agent."
echo "The cloud agent will recommend the optimal model for your hardware."
