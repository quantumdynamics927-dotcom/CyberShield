import click
import torch
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
import yaml
import os
import sys

from slm.cyberlab.model import CyberLabSLM
from slm.cyberlab.preprocessing import TokenizerWrapper, DataProcessor
from slm.llm import LLMProvider

console = Console()


def load_llm_provider(config: dict, provider: str = None, api_key: str = None,
                      model: str = None, offline: bool = False):
    """Load and configure LLM provider from config or CLI options."""
    llm_config = config.get("llm", {})

    # CLI options override config
    provider = provider or llm_config.get("provider", "anthropic")
    api_key = api_key or llm_config.get("api_key", "").replace("${", "").replace("}", "")
    model = model or llm_config.get("model")

    # Expand env vars in api_key
    if api_key.startswith("$"):
        api_key = os.environ.get(api_key[1:], "")

    if offline or llm_config.get("offline_mode", False):
        console.print("[yellow]Running in offline mode - using cached responses[/]")
        return None

    try:
        if provider == "anthropic":
            from slm.llm.anthropic import AnthropicProvider
            return AnthropicProvider(api_key=api_key, model=model)
        elif provider == "openai":
            from slm.llm.openai import OpenAIProvider
            return OpenAIProvider(api_key=api_key, model=model)
        elif provider == "ollama":
            from slm.llm.ollama import OllamaProvider
            endpoint = llm_config.get("endpoint", "http://localhost:11434")
            return OllamaProvider(endpoint=endpoint, model=model)
        else:
            console.print(f"[red]Unknown provider: {provider}[/]")
            return None
    except Exception as e:
        console.print(f"[red]Failed to initialize provider: {e}[/]")
        return None


@click.group()
@click.option('--config', '-c', type=click.Path(exists=False),
              help='Path to configuration file')
@click.option('--provider', '-p', type=click.Choice(['anthropic', 'openai', 'ollama']),
              help='LLM provider to use')
@click.option('--api-key', type=str, help='API key for the LLM provider')
@click.option('--model', '-m', type=str, help='Model to use')
@click.option('--offline', is_flag=True, help='Run in offline mode with cached responses')
@click.pass_context
def cli(ctx, config, provider, api_key, model, offline):
    """CyberLab Assistant CLI tools.

    Configure your LLM provider using config/config.yaml or CLI options.
    Supported providers: anthropic, openai, ollama
    """
    # Default config path - try multiple locations
    if config is None:
        for path in ['config/config.yaml', 'slm/config/config.yaml']:
            if Path(path).exists():
                config = path
                break
        else:
            config = 'slm/config/config.yaml'  # Default even if not exists

    # Load configuration
    config_path = Path(config)
    if config_path.exists():
        with open(config_path) as f:
            ctx.obj = yaml.safe_load(f)
    else:
        console.print(f"[yellow]Warning: Config file not found at {config}, using defaults[/]")
        ctx.obj = {}

    # Load LLM provider
    ctx.obj['llm_provider'] = load_llm_provider(
        ctx.obj, provider, api_key, model, offline
    )
    ctx.obj['offline_mode'] = offline
    ctx.obj['config_path'] = config

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--model-config', '-c', type=click.Path(exists=False), default='slm/config/config.yaml')
@click.option('--output-dir', '-o', type=click.Path(), default='models')
@click.option('--vocab-size', '-v', type=int, default=8000)
def train_tokenizer(input_file, model_config, output_dir, vocab_size):
    """Train a new tokenizer model."""
    with console.status("[bold green]Training tokenizer..."):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize and train tokenizer
        tokenizer = TokenizerWrapper(None)
        model_prefix = output_dir / "cyberlab_tokenizer"
        tokenizer.train(str(input_file), str(model_prefix), vocab_size)

        # Update config if it exists
        config_path = Path(model_config)
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)

            config['tokenizer']['model_path'] = str(model_prefix) + ".model"
            config['tokenizer']['vocab_size'] = vocab_size

            with open(config_path, 'w') as f:
                yaml.dump(config, f)
        else:
            console.print(f"[yellow]Warning: Config file not found at {model_config}[/]")

    console.print("[bold green]✓[/] Tokenizer training completed!")

@cli.command()
@click.argument('train_file', type=click.Path(exists=True))
@click.option('--model-config', '-c', type=click.Path(exists=False), default='slm/config/config.yaml')
@click.option('--epochs', '-e', type=int, default=10)
@click.option('--batch-size', '-b', type=int, default=32)
@click.option('--learning-rate', '-lr', type=float, default=5e-5)
def train_model(train_file, model_config, epochs, batch_size, learning_rate):
    """Train the CyberLab SLM model."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load configuration
    with open(model_config) as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    tokenizer = TokenizerWrapper(config['tokenizer']['model_path'])
    model = CyberLabSLM(vocab_size=tokenizer.vocab_size, **config['model'])
    model.to(device)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    processor = DataProcessor(tokenizer, config['model']['max_seq_length'])
    
    # Load training data
    with open(train_file) as f:
        train_data = f.readlines()
    
    with Progress() as progress:
        epoch_task = progress.add_task("[red]Epochs...", total=epochs)
        
        for epoch in range(epochs):
            batch_task = progress.add_task(f"[green]Epoch {epoch + 1}...", total=len(train_data))
            
            for i in range(0, len(train_data), batch_size):
                batch_texts = train_data[i:i + batch_size]
                batch = processor.prepare_batch(batch_texts)
                
                # Move batch to device
                inputs = {k: v.to(device) for k, v in batch.items()}
                
                # Forward pass
                outputs = model(**inputs)
                loss = torch.nn.functional.cross_entropy(outputs.view(-1, tokenizer.vocab_size), 
                                                       inputs['input_ids'].view(-1))
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                progress.update(batch_task, advance=len(batch_texts))
            
            progress.update(epoch_task, advance=1)
    
    # Save model
    save_path = Path(config['model']['weights_path'])
    save_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), save_path)
    
    console.print("[bold green]✓[/] Model training completed!")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--log-type', '-t', type=click.Choice(['nmap', 'nikto', 'wireshark', 'tcpdump', 'metasploit']), required=True)
@click.option('--model-config', '-c', type=click.Path(exists=False), default='slm/config/config.yaml')
@click.pass_context
def analyze(ctx, input_file, log_type, model_config):
    """Analyze a security log file using cloud LLM."""
    from slm.cyberlab.preprocessing import SecurityLogParser

    # Get config from context
    cli_config = ctx.obj
    llm_provider = cli_config.get('llm_provider')
    offline_mode = cli_config.get('offline_mode', False)

    # Load configuration
    with open(model_config) as f:
        config = yaml.safe_load(f)

    # If LLM provider is available, use it for enhanced analysis
    if llm_provider and llm_provider.is_available():
        with open(input_file) as f:
            content = f.read()

        # Build prompt for the LLM
        prompt = f"""You are a cybersecurity expert analyzing {log_type} scan results.

Analyze the following log output and provide:
1. Severity assessment (critical, high, medium, low, info)
2. Key findings (list of security issues discovered)
3. Recommendations (actionable steps to address issues)

Log content:
```{content}
```

Provide your analysis in JSON format:
{{
    "severity": "...",
    "findings": ["..."],
    "recommendations": ["..."]
}}"""

        with console.status("[bold green]Analyzing with cloud LLM..."):
            try:
                response = llm_provider.complete(prompt)

                # Try to parse JSON from response
                import json
                import re

                # Extract JSON from response
                json_match = re.search(r'\{[\s\S]*\}', response.content)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    # Fallback if JSON parsing fails
                    analysis = {
                        "severity": "unknown",
                        "findings": [response.content],
                        "recommendations": []
                    }
            except Exception as e:
                console.print(f"[yellow]Cloud LLM analysis failed: {e}[/]")
                analysis = _analyze_local(config, input_file, log_type)
    else:
        # Fall back to local model
        if offline_mode:
            console.print("[yellow]Using offline mode - local model[/]")
        else:
            console.print("[yellow]Cloud LLM unavailable, falling back to local model[/]")
        analysis = _analyze_local(config, input_file, log_type)

    # Display results
    console.print("\n[bold]Analysis Results[/]")
    console.print(f"Severity: {analysis.get('severity', 'unknown')}")

    if analysis.get('findings'):
        console.print("\n[bold]Findings:[/]")
        for finding in analysis['findings']:
            console.print(f"• {finding}")

    if analysis.get('recommendations'):
        console.print("\n[bold]Recommendations:[/]")
        for rec in analysis['recommendations']:
            console.print(f"• {rec}")


def _analyze_local(config, input_file, log_type):
    """Fallback to local model analysis."""
    from slm.cyberlab.model import CyberLabSLM as LocalCyberLabSLM

    # Check if tokenizer model exists
    tokenizer_path = config.get('tokenizer', {}).get('model_path', 'models/cyberlab_tokenizer.model')
    if not Path(tokenizer_path).exists():
        return {
            "severity": "unknown",
            "findings": ["Local model not trained - tokenizer not found"],
            "recommendations": ["Run 'cyberlab train-tokenizer' to train the tokenizer", "Or use cloud LLM provider"]
        }

    tokenizer = TokenizerWrapper(tokenizer_path)
    model = LocalCyberLabSLM(vocab_size=tokenizer.vocab_size, **config['model'])

    weights_path = Path(config['model']['weights_path'])
    if weights_path.exists():
        model.load_state_dict(torch.load(weights_path))
    model.eval()

    parser = SecurityLogParser(config['parser']['patterns_file'])

    with open(input_file) as f:
        content = f.read()

    parsed_content = getattr(parser, f"parse_{log_type}_output")(content)
    return model.analyze_security_log(content)

if __name__ == '__main__':
    cli()
