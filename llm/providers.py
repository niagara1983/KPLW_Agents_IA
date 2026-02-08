"""
LLM Provider Implementations
Supports Anthropic Claude, OpenAI GPT, Azure OpenAI, and Ollama (local models)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import os
import time


@dataclass
class LLMRequest:
    """Request structure for LLM calls."""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    model: str = "claude-sonnet-4-5-20250929"
    images: Optional[List[bytes]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Response structure from LLM calls."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency_ms: int
    provider: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    def supports_vision(self) -> bool:
        """Check if provider supports vision/image understanding."""
        pass

    @abstractmethod
    def call(self, request: LLMRequest) -> LLMResponse:
        """Execute LLM call."""
        pass

    @abstractmethod
    def get_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for token usage."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider with vision support."""

    # Pricing per million tokens (as of Feb 2026)
    PRICING = {
        "claude-opus-4-5-20251101": {"input": 15.0, "output": 75.0},
        "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
        "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
    }

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.available = True
        except ImportError:
            print("[WARNING] Anthropic library not installed. Run: pip install anthropic")
            self.available = False
        except Exception as e:
            print(f"[WARNING] Failed to initialize Anthropic client: {e}")
            self.available = False

    @property
    def name(self) -> str:
        return "anthropic"

    def supports_vision(self) -> bool:
        return True

    def call(self, request: LLMRequest) -> LLMResponse:
        """Execute Anthropic API call with optional vision support."""
        if not self.available:
            raise RuntimeError("Anthropic provider not available")

        start_time = time.time()

        # Build message content
        if request.images:
            # Vision mode: multimodal message
            content = [{"type": "text", "text": request.prompt}]

            for img_bytes in request.images:
                import base64
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",  # Assume PNG, adjust if needed
                        "data": img_b64
                    }
                })

            messages = [{"role": "user", "content": content}]
        else:
            # Text-only mode
            messages = [{"role": "user", "content": request.prompt}]

        # Make API call
        response = self.client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system=request.system_prompt if request.system_prompt else "",
            messages=messages
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Calculate cost
        cost = self.get_cost(
            response.usage.input_tokens,
            response.usage.output_tokens,
            request.model
        )

        return LLMResponse(
            content=response.content[0].text,
            model=request.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost=cost,
            latency_ms=latency_ms,
            provider=self.name
        )

    def get_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for Anthropic API usage."""
        pricing = self.PRICING.get(model, self.PRICING["claude-sonnet-4-5-20250929"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider with vision support (GPT-4V)."""

    # Pricing per million tokens (as of Feb 2026)
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.available = True
        except ImportError:
            print("[WARNING] OpenAI library not installed. Run: pip install openai")
            self.available = False
        except Exception as e:
            print(f"[WARNING] Failed to initialize OpenAI client: {e}")
            self.available = False

    @property
    def name(self) -> str:
        return "openai"

    def supports_vision(self) -> bool:
        return True

    def call(self, request: LLMRequest) -> LLMResponse:
        """Execute OpenAI API call with optional vision support."""
        if not self.available:
            raise RuntimeError("OpenAI provider not available")

        start_time = time.time()

        # Build messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        if request.images:
            # Vision mode: multimodal message
            import base64
            content = [{"type": "text", "text": request.prompt}]

            for img_bytes in request.images:
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_b64}"
                    }
                })

            messages.append({"role": "user", "content": content})
        else:
            # Text-only mode
            messages.append({"role": "user", "content": request.prompt})

        # Make API call
        response = self.client.chat.completions.create(
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Calculate cost
        cost = self.get_cost(
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
            request.model
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=request.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            cost=cost,
            latency_ms=latency_ms,
            provider=self.name
        )

    def get_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for OpenAI API usage."""
        pricing = self.PRICING.get(model, self.PRICING["gpt-4o"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost


class AzureProvider(LLMProvider):
    """Azure OpenAI provider."""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")

        try:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=api_key or os.getenv("AZURE_OPENAI_KEY"),
                azure_endpoint=self.endpoint,
                api_version="2024-02-15-preview"
            )
            self.available = True
        except ImportError:
            print("[WARNING] OpenAI library not installed for Azure. Run: pip install openai")
            self.available = False
        except Exception as e:
            print(f"[WARNING] Failed to initialize Azure OpenAI client: {e}")
            self.available = False

    @property
    def name(self) -> str:
        return "azure"

    def supports_vision(self) -> bool:
        return True

    def call(self, request: LLMRequest) -> LLMResponse:
        """Execute Azure OpenAI API call."""
        if not self.available:
            raise RuntimeError("Azure provider not available")

        # Azure uses same API as OpenAI
        start_time = time.time()

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        response = self.client.chat.completions.create(
            model=request.model,  # This should be the deployment name in Azure
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Azure pricing is same as OpenAI for equivalent models
        cost = OpenAIProvider.PRICING.get(request.model, {"input": 2.5, "output": 10.0})
        input_cost = (response.usage.prompt_tokens / 1_000_000) * cost["input"]
        output_cost = (response.usage.completion_tokens / 1_000_000) * cost["output"]

        return LLMResponse(
            content=response.choices[0].message.content,
            model=request.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            cost=input_cost + output_cost,
            latency_ms=latency_ms,
            provider=self.name
        )

    def get_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for Azure OpenAI usage."""
        # Use OpenAI pricing as baseline
        pricing = OpenAIProvider.PRICING.get(model, {"input": 2.5, "output": 10.0})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost


class OllamaProvider(LLMProvider):
    """Ollama provider for local models (free)."""

    def __init__(self, base_url: Optional[str] = None, **kwargs):
        super().__init__(api_key=None, **kwargs)
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        try:
            import requests
            self.requests = requests
            # Test connection
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self.available = response.status_code == 200
        except ImportError:
            print("[WARNING] Requests library not installed. Run: pip install requests")
            self.available = False
        except Exception as e:
            print(f"[INFO] Ollama not available at {self.base_url}: {e}")
            self.available = False

    @property
    def name(self) -> str:
        return "ollama"

    def supports_vision(self) -> bool:
        return True  # llava models support vision

    def call(self, request: LLMRequest) -> LLMResponse:
        """Execute Ollama API call."""
        if not self.available:
            raise RuntimeError("Ollama provider not available. Is Ollama running?")

        start_time = time.time()

        # Build prompt
        full_prompt = request.prompt
        if request.system_prompt:
            full_prompt = f"{request.system_prompt}\n\n{request.prompt}"

        # Make API call
        response = self.requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": request.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            },
            timeout=300
        )

        response.raise_for_status()
        result = response.json()

        latency_ms = int((time.time() - start_time) * 1000)

        # Ollama is free (local)
        return LLMResponse(
            content=result["response"],
            model=request.model,
            input_tokens=result.get("prompt_eval_count", 0),
            output_tokens=result.get("eval_count", 0),
            cost=0.0,  # Local model, no cost
            latency_ms=latency_ms,
            provider=self.name
        )

    def get_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Ollama is free (local)."""
        return 0.0


class ProviderFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create(provider_name: str, **config) -> LLMProvider:
        """Create provider instance by name."""
        providers = {
            "anthropic": AnthropicProvider,
            "openai": OpenAIProvider,
            "azure": AzureProvider,
            "ollama": OllamaProvider,
        }

        if provider_name not in providers:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available: {', '.join(providers.keys())}"
            )

        provider_class = providers[provider_name]
        return provider_class(**config)

    @staticmethod
    def create_from_config(config_dict: Dict[str, Any]) -> LLMProvider:
        """Create provider from configuration dictionary."""
        provider_name = config_dict.get("provider", "anthropic")
        return ProviderFactory.create(provider_name, **config_dict)
