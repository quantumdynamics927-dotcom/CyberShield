"""OpenAI provider implementation."""

import os
from typing import Optional, Dict, Any, List
from slm.llm.base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: int = 4096,
        **kwargs
    ):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o)
            base_url: Custom base URL for OpenAI-compatible APIs
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
        """
        super().__init__(api_key=api_key, model=model, base_url=base_url)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model or self.DEFAULT_MODEL
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.extra_kwargs = kwargs

    def _get_client(self):
        """Get or create OpenAI client."""
        try:
            from openai import OpenAI

            if self.base_url:
                return OpenAI(api_key=self.api_key, base_url=self.base_url)
            return OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to OpenAI.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse object with the model's response
        """
        if not self.is_available():
            raise RuntimeError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable or pass api_key."
            )

        client = self._get_client()

        # Make API call
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature"),
            top_p=kwargs.get("top_p"),
            stop=kwargs.get("stop"),
        )

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            stop_reason=response.choices[0].finish_reason,
            raw_response=response.model_dump(),
        )

    def complete(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """Send a completion request to OpenAI.

        Args:
            prompt: The prompt to complete
            **kwargs: Additional parameters

        Returns:
            LLMResponse object with the model's response
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)

    def is_available(self) -> bool:
        """Check if OpenAI API is available.

        Returns:
            True if API key is configured, False otherwise
        """
        return bool(self.api_key)

    def get_model_name(self) -> str:
        """Get the model name being used."""
        return self.model
