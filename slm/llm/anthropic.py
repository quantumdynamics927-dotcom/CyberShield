"""Anthropic Claude provider implementation."""

import os
from typing import Optional, Dict, Any, List
from slm.llm.base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        **kwargs
    ):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-sonnet-4-20250514)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
        """
        super().__init__(api_key=api_key, model=model)
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens
        self.extra_kwargs = kwargs

    def _get_client(self):
        """Get or create Anthropic client."""
        try:
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            )

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to Anthropic.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse object with the model's response
        """
        if not self.is_available():
            raise RuntimeError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key."
            )

        client = self._get_client()

        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append(msg)

        # Make API call
        response = client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            messages=anthropic_messages,
            system=system_message,
            temperature=kwargs.get("temperature"),
            top_p=kwargs.get("top_p"),
            stop_sequences=kwargs.get("stop_sequences"),
        )

        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            stop_reason=response.stop_reason,
            raw_response=response.model_dump(),
        )

    def complete(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """Send a completion request to Anthropic.

        Args:
            prompt: The prompt to complete
            **kwargs: Additional parameters

        Returns:
            LLMResponse object with the model's response
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)

    def is_available(self) -> bool:
        """Check if Anthropic API is available.

        Returns:
            True if API key is configured, False otherwise
        """
        return bool(self.api_key)

    def get_model_name(self) -> str:
        """Get the model name being used."""
        return self.model
