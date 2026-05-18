import sys
import re

f = sys.argv[1]
with open(f) as fh:
    lines = fh.readlines()

out = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Skip the hallucinated comment lines
    if "The pi settings command creates" in line or "if it doesn't exist yet. No manual file editing needed." in line:
        i += 1
        continue
    
    # Replace hallucinated Step 1 for each provider
    if "pi settings providers ollama apiKey YOUR_OLLAMA_CLOUD_KEY" in line:
        out.append('# Step 1: Add your API key\n')
        out.append('export OLLAMA_CLOUD_KEY="your-key-here"\n')
        out.append('pi --provider ollama --model qwen3.5:cloud --api-key $OLLAMA_CLOUD_KEY "Hello"\n')
        i += 1
        continue
    
    if "pi settings providers google apiKey YOUR_GEMINI_API_KEY" in line:
        out.append('# Step 1: Add your API key\n')
        out.append('export GEMINI_API_KEY="your-key-here"\n')
        out.append('pi --provider google --model gemini-2.5-pro --api-key $GEMINI_API_KEY "Hello"\n')
        i += 1
        continue
    
    if "pi settings providers anthropic apiKey YOUR_ANTHROPIC_API_KEY" in line:
        out.append('# Step 1: Add your API key\n')
        out.append('export ANTHROPIC_API_KEY="your-key-here"\n')
        out.append('pi --provider anthropic --model claude-sonnet-4-6 --api-key $ANTHROPIC_API_KEY "Hello"\n')
        i += 1
        continue
    
    if "pi settings providers openai apiKey YOUR_OPENAI_API_KEY" in line:
        out.append('# Step 1: Add your API key\n')
        out.append('export OPENAI_API_KEY="your-key-here"\n')
        out.append('pi --provider openai --model gpt-4o --api-key $OPENAI_API_KEY "Hello"\n')
        i += 1
        continue
    
    # Replace hallucinated Step 2 lines
    if "pi settings models add ollama-cloud/qwen3.5:cloud" in line:
        out.append('# Or for larger models:\n')
        out.append('# pi --provider ollama --model llama3.1:cloud --api-key $OLLAMA_CLOUD_KEY "Hello"\n')
        out.append('# Or for reasoning tasks:\n')
        out.append('# pi --provider ollama --model deepseek-r1:cloud --api-key $OLLAMA_CLOUD_KEY "Hello"\n')
        i += 1
        continue
    
    if "pi settings models add google/gemini-2.5-pro" in line:
        out.append('# Or for flash (faster, cheaper):\n')
        out.append('# pi --provider google --model gemini-2.5-flash --api-key $GEMINI_API_KEY "Hello"\n')
        i += 1
        continue
    
    if "pi settings models add anthropic/claude-sonnet-4-6" in line:
        out.append('# Or for opus (highest quality, more expensive):\n')
        out.append('# pi --provider anthropic --model claude-opus-4 --api-key $ANTHROPIC_API_KEY "Hello"\n')
        i += 1
        continue
    
    if "pi settings models add openai/gpt-4o" in line:
        out.append('# Or for cheaper option:\n')
        out.append('# pi --provider openai --model gpt-4o-mini --api-key $OPENAI_API_KEY "Hello"\n')
        i += 1
        continue
    
    # Skip all the "pi settings models add" fallback comment lines
    if line.strip().startswith('# pi settings models add'):
        i += 1
        continue
    
    # Detect and skip the "Prefer Manual Setup?" section entirely
    if "**Prefer Manual Setup?**" in line:
        # Skip until we find "**Step 2: Verify the model works**"
        while i < len(lines) and "**Step 2: Verify the model works**" not in lines[i]:
            i += 1
        if i < len(lines):
            out.append('---\n\n')
            out.append(lines[i])  # Append the "**Step 2: Verify...**" line
        i += 1
        continue
    
    # Detect and skip "Where API Keys Are Stored" section
    if "**Where API Keys Are Stored:**" in line:
        # Skip until next section starting with **
        while i < len(lines):
            i += 1
            if i < len(lines) and lines[i].strip().startswith("**"):
                out.append(lines[i])
                i += 1
                break
        continue
    
    out.append(line)
    i += 1

with open(f, 'w') as fh:
    fh.writelines(out)

# Verify
with open(f) as fh:
    content = fh.read()
print("Remaining 'pi settings providers':", content.count('pi settings providers'))
print("Remaining 'pi settings models add':", content.count('pi settings models add'))
print("Done.")
