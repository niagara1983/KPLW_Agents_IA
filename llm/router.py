"""
Model Router - Intelligent task-based LLM selection
Routes requests to optimal model/provider based on task characteristics and budget
"""

from typing import Dict, Optional
from dataclasses import dataclass
from .providers import LLMProvider, LLMRequest, LLMResponse, ProviderFactory


@dataclass
class CostTracker:
    """Track API costs and enforce budget limits."""

    budget_limit: Optional[float] = None
    current_cost: float = 0.0
    calls: list = None

    def __post_init__(self):
        if self.calls is None:
            self.calls = []

    def track_call(self, response: LLMResponse) -> None:
        """Record API call cost."""
        self.current_cost += response.cost
        self.calls.append({
            "provider": response.provider,
            "model": response.model,
            "cost": response.cost,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "latency_ms": response.latency_ms
        })

    def check_budget(self, estimated_cost: float = 0.0) -> bool:
        """Check if within budget limit."""
        if self.budget_limit is None:
            return True
        return (self.current_cost + estimated_cost) <= self.budget_limit

    def get_remaining_budget(self) -> Optional[float]:
        """Get remaining budget."""
        if self.budget_limit is None:
            return None
        return max(0.0, self.budget_limit - self.current_cost)

    def get_summary(self) -> Dict:
        """Get cost summary."""
        return {
            "total_cost": self.current_cost,
            "budget_limit": self.budget_limit,
            "remaining": self.get_remaining_budget(),
            "num_calls": len(self.calls),
            "calls": self.calls
        }


class ModelRouter:
    """Routes LLM requests to optimal model based on task characteristics."""

    def __init__(self, providers: Dict[str, LLMProvider], cost_tracker: Optional[CostTracker] = None):
        """
        Initialize router with available providers.

        Args:
            providers: Dict mapping provider names to LLMProvider instances
            cost_tracker: Optional cost tracker for budget enforcement
        """
        self.providers = providers
        self.cost_tracker = cost_tracker or CostTracker()

        # Default routing configuration
        self.routing_config = {
            "TIMBO": {
                "analysis": "claude-opus-4-5-20251101",
                "extraction": "claude-sonnet-4-5-20250929"
            },
            "ZAT": {
                "scenario_design": "claude-sonnet-4-5-20250929",
                "financial": "claude-opus-4-5-20251101"
            },
            "MARY": {
                "narrative": "claude-sonnet-4-5-20250929",
                "compliance": "claude-haiku-4-5-20251001",
                "tables": "claude-haiku-4-5-20251001"
            },
            "RANA": {
                "evaluation": "claude-opus-4-5-20251101"
            }
        }

    def route_request(
        self,
        request: LLMRequest,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None,
        preferred_provider: Optional[str] = None
    ) -> LLMResponse:
        """
        Route request to optimal provider/model.

        Args:
            request: The LLM request
            agent_name: Name of agent making request (TIMBO, ZAT, MARY, RANA)
            task_type: Type of task (analysis, extraction, scenario_design, etc.)
            preferred_provider: Override provider selection

        Returns:
            LLMResponse from the selected provider
        """
        # Select model based on agent and task type
        model = self._select_model(agent_name, task_type, request.model)
        request.model = model

        # Select provider
        provider_name = preferred_provider or self._select_provider(model)

        if provider_name not in self.providers:
            # Fallback to first available provider
            provider_name = next(iter(self.providers.keys()))
            print(f"[WARNING] Provider {preferred_provider} not available. Using {provider_name}")

        provider = self.providers[provider_name]

        # Check budget before calling
        if not self.cost_tracker.check_budget():
            raise BudgetExceededError(
                f"Budget limit of ${self.cost_tracker.budget_limit:.2f} would be exceeded. "
                f"Current cost: ${self.cost_tracker.current_cost:.2f}"
            )

        # Make the call
        try:
            response = provider.call(request)
            self.cost_tracker.track_call(response)
            return response
        except Exception as e:
            # Try fallback provider if available
            if len(self.providers) > 1:
                print(f"[WARNING] Provider {provider_name} failed: {e}. Trying fallback...")
                fallback_provider = self._get_fallback_provider(provider_name)
                if fallback_provider:
                    response = fallback_provider.call(request)
                    self.cost_tracker.track_call(response)
                    return response
            raise

    def _select_model(
        self,
        agent_name: Optional[str],
        task_type: Optional[str],
        default_model: str
    ) -> str:
        """Select optimal model based on agent and task."""
        if agent_name and task_type:
            # Check routing config
            agent_config = self.routing_config.get(agent_name, {})
            model = agent_config.get(task_type)
            if model:
                return model

        # Check if budget is low, use cheaper model
        remaining = self.cost_tracker.get_remaining_budget()
        if remaining is not None and remaining < 1.0:
            # Budget constraint: use cheaper model
            return "claude-haiku-4-5-20251001"  # Cheapest capable model

        return default_model

    def _select_provider(self, model: str) -> str:
        """Select provider based on model name."""
        # Claude models → Anthropic
        if "claude" in model.lower():
            return "anthropic"
        # GPT models → OpenAI
        elif "gpt" in model.lower():
            return "openai"
        # Default to first available
        else:
            return next(iter(self.providers.keys()))

    def _get_fallback_provider(self, failed_provider: str) -> Optional[LLMProvider]:
        """Get fallback provider when primary fails."""
        # Priority order: anthropic → openai → ollama → azure
        fallback_order = ["anthropic", "openai", "ollama", "azure"]

        for provider_name in fallback_order:
            if provider_name != failed_provider and provider_name in self.providers:
                return self.providers[provider_name]

        return None

    def update_routing_config(self, agent_name: str, task_type: str, model: str) -> None:
        """Update routing configuration."""
        if agent_name not in self.routing_config:
            self.routing_config[agent_name] = {}
        self.routing_config[agent_name][task_type] = model

    def get_cost_summary(self) -> Dict:
        """Get cost tracking summary."""
        return self.cost_tracker.get_summary()


class BudgetExceededError(Exception):
    """Raised when budget limit is exceeded."""
    pass
