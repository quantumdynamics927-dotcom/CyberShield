# CyberLab Assistant Installation Guide

## Prerequisites

- **Python 3.9 or later** - [Download from python.org](https://www.python.org/downloads/)
- **pip** - Usually included with Python

## Installation Methods

### Method 1: pip install (Recommended)

```bash
# Install the package
pip install cyberlab-assistant

# Or install with all features
pip install cyberlab-assistant[all]
```

### Method 2: Development Installation

```bash
# Clone or navigate to the repository
cd cyberlab-assistant

# Install in development mode
pip install -e .
```

### Method 3: Windows Portable

```bash
# Run directly with the batch file
.\cyberlab.bat --help
```

## Configuration

### 1. Set up LLM Provider

Edit `config/config.yaml` to configure your LLM provider:

```yaml
llm:
  provider: "anthropic"  # Options: anthropic, openai, ollama
  api_key: "${ANTHROPIC_API_KEY}"  # Or set directly
  model: "claude-sonnet-4-20250514"
```

### 2. Environment Variables

Set your API key as an environment variable:

```powershell
# PowerShell
$env:ANTHROPIC_API_KEY = "your-api-key-here"

# Command Prompt
set ANTHROPIC_API_KEY=your-api-key-here
```

### Supported Providers

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| Anthropic Claude | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| OpenAI GPT | `OPENAI_API_KEY` | gpt-4o |
| Ollama (local) | `OLLAMA_ENDPOINT` | llama3 |

## Quick Start

```bash
# Show help
cyberlab --help

# Analyze a security log
cyberlab analyze nmap_scan.xml -t nmap

# Use specific provider
cyberlab analyze log.txt -t nmap --provider anthropic --model claude-sonnet-4-20250514

# Run in offline mode (uses local model)
cyberlab analyze log.txt -t nmap --offline

# Train tokenizer
cyberlab train-tokenizer data/training.txt

# Train model
cyberlab train-model data/training.txt
```

## Windows-Specific Notes

### PowerShell Support

The tool works with both Command Prompt and PowerShell. For best results, use PowerShell.

### Tool Equivalents

Common Linux tools are automatically converted to Windows equivalents:
- `ls` → `dir`
- `cat` → `type`
- `grep` → `findstr`
- `ps` → `tasklist`

### ANSI Colors

Colors should work automatically. If colors are not showing:
1. Make sure you're using a modern terminal (Windows Terminal recommended)
2. Or run: `set TERM=dumb`

## Troubleshooting

### "Python not found"

Install Python from [python.org](https://www.python.org/downloads/) and ensure it's in your PATH.

### "API key not configured"

Set the appropriate environment variable for your provider:
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

### "Module not found"

Reinstall the package:
```bash
pip install -e .
```

### "torch not found" (offline mode)

Install the local model dependencies:
```bash
pip install torch sentencepiece
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black slm/
ruff check slm/
```
