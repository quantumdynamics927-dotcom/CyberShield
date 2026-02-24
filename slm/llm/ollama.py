"""Ollama local LLM provider implementation."""

import os
import requests
from typing import Optional, Dict, Any, List
from slm.llm.base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    DEFAULT_MODEL = "llama3"
    DEFAULT_ENDPOINT = "http://localhost:11434"

    def __init__(
        self,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """Initialize Ollama provider.

        Args:
            endpoint: Ollama API endpoint (default: http://localhost:11434)
            model: Model to use (default: llama3)
            **kwargs: Additional parameters
        """
        super().__init__(base_url=endpoint)
        self.endpoint = endpoint or os.environ.get("OLLAMA_ENDPOINT", self.DEFAULT_ENDPOINT)
        self.model = model or self.DEFAULT_MODEL
        self.extra_kwargs = kwargs

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters (temperature, options, etc.)

        Returns:
            LLMResponse object with the model's response
        """
        if not self.is_available():
            raise RuntimeError(
                f"Ollama not available at {self.endpoint}. "
                "Make sure Ollama is running."
            )

        url = f"{self.endpoint}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        # Add optional parameters
        if "temperature" in kwargs:
            options = payload.get("options", {})
            options["temperature"] = kwargs["temperature"]
            payload["options"] = options

        response = requests.post(url, json=payload, timeout=120)

        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.text}")

        data = response.json()

        return LLMResponse(
            content=data.get("message", {}).get("content", ""),
            model=self.model,
            usage=None,
            stop_reason=data.get("done_reason"),
            raw_response=data,
        )

    def complete(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """Send a completion request to Ollama.

        Args:
            prompt: The prompt to complete
            **kwargs: Additional parameters

        Returns:
            LLMResponse object with the model's response
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)

    def is_available(self) -> bool:
        """Check if Ollama is available.

        Returns:
            True if Ollama is running and accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_model_name(self) -> str:
        """Get the model name being used."""
        return self.model

    def list_models(self) -> List[str]:
        """List available models in Ollama.

        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except requests.RequestException:
            pass
        return []
