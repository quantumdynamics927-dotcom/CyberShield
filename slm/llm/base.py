"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import os


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    stop_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize LLM provider.

        Args:
            api_key: API key for the provider
            model: Model identifier to use
            base_url: Custom base URL (for Ollama, proxies, etc.)
            **kwargs: Additional provider-specific parameters
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model
        self.base_url = base_url
        self.extra_kwargs = kwargs

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            LLMResponse object with the model's response
        """
        pass

    @abstractmethod
    def complete(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """Send a completion request.

        Args:
            prompt: The prompt to complete
            **kwargs: Additional parameters

        Returns:
            LLMResponse object with the model's response
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured.

        Returns:
            True if provider can be used, False otherwise
        """
        pass

    def get_model_name(self) -> str:
        """Get the model name being used."""
        return self.model or "unknown"

    @staticmethod
    def from_config(config: Dict[str, Any]) -> "LLMProvider":
        """Create a provider from configuration dict.

        Args:
            config: Configuration dictionary with provider settings

        Returns:
            LLMProvider instance
        """
        provider_type = config.get("provider", "anthropic").lower()

        if provider_type == "anthropic":
            from slm.llm.anthropic import AnthropicProvider
            return AnthropicProvider(
                api_key=config.get("api_key"),
                model=config.get("model", "claude-sonnet-4-20250514")
            )
        elif provider_type == "openai":
            from slm.llm.openai import OpenAIProvider
            return OpenAIProvider(
                api_key=config.get("api_key"),
                model=config.get("model", "gpt-4o")
            )
        elif provider_type == "ollama":
            from slm.llm.ollama import OllamaProvider
            return OllamaProvider(
                endpoint=config.get("endpoint", "http://localhost:11434"),
                model=config.get("model", "llama3")
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
