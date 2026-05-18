import sys
import re

f = sys.argv[1]
with open(f) as fh:
    text = fh.read()

# Fix all hallucinated pi settings commands
# Pattern: Step 1 with pi settings providers + Step 2 with pi settings models add
# We'll replace each provider block individually

replacements = [
    # Ollama
    ("""# Step 1: Add your API key to pi
# The pi settings command creates ~/.pi/agent/models.json automatically
# if it doesn't exist yet. No manual file editing needed.
pi settings providers ollama apiKey YOUR_OLLAMA_CLOUD_KEY

# Step 2: Configure the model in pi
pi settings models add ollama-cloud/qwen3.5:cloud
# Or for larger models:
# pi settings models add ollama-cloud/llama3.1:cloud
# Or for reasoning tasks:
# pi settings models add ollama-cloud/deepseek-r1:cloud""",

     """# Step 1: Add your API key
export OLLAMA_CLOUD_KEY="your-key-here"
pi --provider ollama --model qwen3.5:cloud --api-key $OLLAMA_CLOUD_KEY "Hello"
# Or for larger models:
# pi --provider ollama --model llama3.1:cloud --api-key $OLLAMA_CLOUD_KEY "Hello"
# Or for reasoning tasks:
# pi --provider ollama --model deepseek-r1:cloud --api-key $OLLAMA_CLOUD_KEY "Hello""""),

    # Google
    ("""# Step 1: Add your API key to pi
# The pi settings command creates ~/.pi/agent/models.json automatically
# if it doesn't exist yet. No manual file editing needed.
pi settings providers google apiKey YOUR_GEMINI_API_KEY

# Step 2: Configure the model in pi
pi settings models add google/gemini-2.5-pro
# Or for flash (faster, cheaper):
# pi settings models add google/gemini-2.5-flash""",

     """# Step 1: Add your API key
export GEMINI_API_KEY="your-key-here"
pi --provider google --model gemini-2.5-pro --api-key $GEMINI_API_KEY "Hello"
# Or for flash (faster, cheaper):
# pi --provider google --model gemini-2.5-flash --api-key $GEMINI_API_KEY "Hello""""),

    # Anthropic
    ("""# Step 1: Add your API key to pi
# The pi settings command creates ~/.pi/agent/models.json automatically
# if it doesn't exist yet. No manual file editing needed.
pi settings providers anthropic apiKey YOUR_ANTHROPIC_API_KEY

# Step 2: Configure the model in pi
pi settings models add anthropic/claude-sonnet-4-6
# Or for opus (highest quality, more expensive):
# pi settings models add anthropic/claude-opus-4""",

     """# Step 1: Add your API key
export ANTHROPIC_API_KEY="your-key-here"
pi --provider anthropic --model claude-sonnet-4-6 --api-key $ANTHROPIC_API_KEY "Hello"
# Or for opus (highest quality, more expensive):
# pi --provider anthropic --model claude-opus-4 --api-key $ANTHROPIC_API_KEY "Hello""""),

    # OpenAI
    ("""# Step 1: Add your API key to pi
# The pi settings command creates ~/.pi/agent/models.json automatically
# if it doesn't exist yet. No manual file editing needed.
pi settings providers openai apiKey YOUR_OPENAI_API_KEY

# Step 2: Configure the model in pi
pi settings models add openai/gpt-4o
# Or for cheaper option:
# pi settings models add openai/gpt-4o-mini""",

     """# Step 1: Add your API key
export OPENAI_API_KEY="your-key-here"
pi --provider openai --model gpt-4o --api-key $OPENAI_API_KEY "Hello"
# Or for cheaper option:
# pi --provider openai --model gpt-4o-mini --api-key $OPENAI_API_KEY "Hello""""),
]

count = 0
for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        count += 1
        print(f"Replaced provider block")
    else:
        print(f"NOT FOUND (checking for partial)...")
        # Debug
        if "pi settings providers" in old and old[:40] in text:
            idx = text.index(old[:40])
            print(f"  Found partial at index {idx}, next 100 chars: {repr(text[idx:idx+100])}")

print(f"Total replacements: {count}")
print(f"Remaining 'pi settings providers': {text.count('pi settings providers')}")

with open(f, 'w') as fh:
    fh.write(text)

print("Done.")
