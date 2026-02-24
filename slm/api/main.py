from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import yaml
from pathlib import Path
import json

# Try to import optional dependencies
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from slm.cyberlab.model import CyberLabSLM
    from slm.cyberlab.preprocessing import TokenizerWrapper, SecurityLogParser, DataProcessor
    HAS_CYBERLAB = True
except ImportError:
    HAS_CYBERLAB = False

app = FastAPI(
    title="CyberLab Assistant API",
    description="API for security log analysis and report generation using cloud LLM",
    version="1.0.0"
)

# Global instances
MODEL: Optional[Any] = None
TOKENIZER: Optional[Any] = None
PARSER: Optional[Any] = None
DATA_PROCESSOR: Optional[Any] = None
LLM_PROVIDER: Optional[Any] = None

class AnalysisRequest(BaseModel):
    content: str
    log_type: str
    cache: bool = True

class AnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    recommendations: List[str]
    severity: str

@app.on_event("startup")
async def startup_event():
    """Initialize model and components on startup."""
    global MODEL, TOKENIZER, PARSER, DATA_PROCESSOR, LLM_PROVIDER

    # Try multiple config paths
    config_path = None
    for path in ["slm/config/config.yaml", "config/config.yaml"]:
        if Path(path).exists():
            config_path = Path(path)
            break

    if not config_path:
        print("Warning: Config file not found, using defaults")
        LLM_PROVIDER = None
        return

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Initialize LLM provider from config
    llm_config = config.get("llm", {})
    provider_type = llm_config.get("provider", "ollama")

    try:
        if provider_type == "ollama":
            from slm.llm.ollama import OllamaProvider
            LLM_PROVIDER = OllamaProvider(
                endpoint=llm_config.get("endpoint", "http://localhost:11434"),
                model=llm_config.get("model", "llama3.1:8b")
            )
        elif provider_type == "anthropic":
            from slm.llm.anthropic import AnthropicProvider
            api_key = llm_config.get("api_key", "")
            if api_key.startswith("${") and api_key.endswith("}"):
                api_key = os.environ.get(api_key[2:-1], "")
            LLM_PROVIDER = AnthropicProvider(api_key=api_key, model=llm_config.get("model"))
        elif provider_type == "openai":
            from slm.llm.openai import OpenAIProvider
            api_key = llm_config.get("api_key", "")
            if api_key.startswith("${") and api_key.endswith("}"):
                api_key = os.environ.get(api_key[2:-1], "")
            LLM_PROVIDER = OpenAIProvider(api_key=api_key, model=llm_config.get("model"))
        else:
            LLM_PROVIDER = None
    except Exception as e:
        print(f"Warning: Failed to initialize LLM provider: {e}")
        LLM_PROVIDER = None

    # Try to initialize local model if LLM provider not available
    if not LLM_PROVIDER or not LLM_PROVIDER.is_available():
        try:
            tokenizer_path = Path(config["tokenizer"]["model_path"])
            if tokenizer_path.exists():
                TOKENIZER = TokenizerWrapper(str(tokenizer_path))
                MODEL = CyberLabSLM(
                    vocab_size=TOKENIZER.vocab_size,
                    **config["model"]
                )
                model_path = Path(config["model"]["weights_path"])
                if model_path.exists():
                    MODEL.load_state_dict(torch.load(model_path))
                MODEL.eval()
                PARSER = SecurityLogParser(config["parser"]["patterns_file"])
                DATA_PROCESSOR = DataProcessor(TOKENIZER, config["model"]["max_seq_length"])
                print("Local model initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize local model: {e}")
            MODEL = None
    
    # Load analysis cache if available
    cache_path = Path(config["cache"]["file_path"])
    if cache_path.exists():
        MODEL.load_cache(str(cache_path))

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_log(request: AnalysisRequest):
    """Analyze security log content using cloud LLM or local model."""
    try:
        # Try cloud LLM first
        if LLM_PROVIDER and LLM_PROVIDER.is_available():
            prompt = f"""You are a cybersecurity expert analyzing {request.log_type} scan results.

Analyze the following log output and provide:
1. Severity assessment (critical, high, medium, low, info)
2. Key findings (list of security issues discovered)
3. Recommendations (actionable steps to address issues)

Log content:
```{request.content}
```

Provide your analysis in JSON format:
{{
    "severity": "...",
    "findings": ["..."],
    "recommendations": ["..."]
}}"""

            response = LLM_PROVIDER.complete(prompt)

            # Parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {
                    "severity": "unknown",
                    "findings": [response.content],
                    "recommendations": []
                }

            return AnalysisResponse(
                analysis=analysis,
                recommendations=analysis.get("recommendations", []),
                severity=analysis.get("severity", "unknown")
            )

        # Fall back to local model
        if not MODEL or not TOKENIZER or not PARSER:
            raise HTTPException(status_code=500, detail="No model available")

        # Parse log based on type
        parsed_content = getattr(PARSER, f"parse_{request.log_type}_output")(request.content)

        # Prepare input for model
        batch = DATA_PROCESSOR.prepare_batch([json.dumps(parsed_content)])

        # Generate analysis
        with torch.no_grad():
            analysis = MODEL.analyze_security_log(request.content)

        return AnalysisResponse(
            analysis=analysis,
            recommendations=analysis.get("recommendations", []),
            severity=analysis.get("severity", "unknown")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/file")
async def analyze_file(
    file: UploadFile = File(...),
    log_type: str = None,
    background_tasks: BackgroundTasks = None
):
    """Analyze uploaded security log file."""
    if not log_type:
        raise HTTPException(status_code=400, detail="Log type must be specified")
    
    content = await file.read()
    content = content.decode()
    
    request = AnalysisRequest(content=content, log_type=log_type)
    return await analyze_log(request)

@app.get("/health")
async def health_check():
    """Check API health status."""
    llm_available = LLM_PROVIDER and LLM_PROVIDER.is_available()
    return {
        "status": "healthy",
        "model_loaded": MODEL is not None,
        "llm_provider": LLM_PROVIDER.get_model_name() if llm_available else None,
        "llm_available": llm_available
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
