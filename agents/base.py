"""
KPLW Agents - Base Classes
Foundation classes for the multi-agent system
"""

import json
from typing import TypedDict, Optional
from datetime import datetime

# Conditional imports
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("[AVERTISSEMENT] Module 'anthropic' non installe. Mode simulation active.")
    print("  Installez avec : pip install anthropic")

# Multi-provider system
try:
    from llm.providers import ProviderFactory, LLMRequest, LLMResponse
    from llm.router import ModelRouter, CostTracker
    MULTI_PROVIDER_AVAILABLE = True
except ImportError:
    MULTI_PROVIDER_AVAILABLE = False
    print("[INFO] Multi-provider system not available. Using legacy Anthropic-only client.")

from config import (
    ANTHROPIC_API_KEY, MODELS, MAX_TOKENS, TEMPERATURE, SIMULATION_MODE,
    DEFAULT_PROVIDER, OPENAI_API_KEY, BUDGET_LIMIT_USD, MODEL_ROUTING
)


# ════════════════════════════════════════════════════════════
# PROJECT STATE
# ════════════════════════════════════════════════════════════

class ProjectState(TypedDict):
    """Shared state between all agents via LangGraph."""
    # Input
    project_brief: str                  # Project brief
    project_id: str                     # Unique identifier
    language: str                       # Detected language (fr/en)

    # Agent outputs
    timbo_analysis: str                 # Requirements (TIMBO)
    zat_blueprint: str                  # Blueprint + scenarios (ZAT)
    mary_deliverable: str               # Deliverable (MARY)
    rana_evaluation: str                # Evaluation (RANA)

    # Workflow control
    rana_score: int                      # Quality score (0-100)
    rana_decision: str                   # VALIDE / MARY / ZAT / TIMBO
    iteration_count: int                 # Iteration counter
    status: str                          # In progress / Valid / Escalate
    workflow_log: list                   # Workflow log

    # Metadata
    started_at: str
    completed_at: str


# ════════════════════════════════════════════════════════════
# LLM CLIENT
# ════════════════════════════════════════════════════════════

class LLMClient:
    """Multi-provider LLM client with simulation support."""

    def __init__(self):
        self.simulation = SIMULATION_MODE
        self.use_multi_provider = MULTI_PROVIDER_AVAILABLE and not SIMULATION_MODE

        if self.use_multi_provider:
            try:
                self._init_multi_provider()
            except Exception as e:
                print(f"[AVERTISSEMENT] Multi-provider init failed: {e}. Using legacy mode.")
                self.use_multi_provider = False
                self._init_legacy()
        else:
            self._init_legacy()

    def _init_multi_provider(self):
        """Initialize multi-provider router."""
        providers = {}

        # Anthropic (primary)
        if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "VOTRE_CLE_API_ICI":
            providers["anthropic"] = ProviderFactory.create("anthropic", api_key=ANTHROPIC_API_KEY)

        # OpenAI
        if OPENAI_API_KEY:
            providers["openai"] = ProviderFactory.create("openai", api_key=OPENAI_API_KEY)

        # Ollama (local)
        try:
            providers["ollama"] = ProviderFactory.create("ollama")
        except:
            pass  # Ollama not available, skip

        if not providers:
            raise RuntimeError("No LLM providers configured")

        # Create cost tracker with budget limit
        self.cost_tracker = CostTracker(budget_limit=BUDGET_LIMIT_USD)

        # Create router
        self.router = ModelRouter(providers=providers, cost_tracker=self.cost_tracker)

        print(f"[INFO] Multi-provider system initialized: {', '.join(providers.keys())}")

    def _init_legacy(self):
        """Initialize legacy Anthropic-only client."""
        if not ANTHROPIC_AVAILABLE:
            self.client = None
            self.simulation = True
        else:
            try:
                self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
                if ANTHROPIC_API_KEY == "VOTRE_CLE_API_ICI":
                    print("[AVERTISSEMENT] Cle API non configuree. Passage en mode simulation.")
                    self.simulation = True
            except Exception as e:
                print(f"[AVERTISSEMENT] Erreur API : {e}. Passage en mode simulation.")
                self.simulation = True
                self.client = None

    def call(self, agent_name: str, system_prompt: str, user_message: str, task_type: str = None) -> str:
        """Call LLM API (multi-provider or legacy) or return simulation."""
        if self.simulation:
            return self._simulate(agent_name, user_message)

        if self.use_multi_provider:
            return self._call_multi_provider(agent_name, system_prompt, user_message, task_type)
        else:
            return self._call_legacy(agent_name, system_prompt, user_message)

    def _call_multi_provider(self, agent_name: str, system_prompt: str, user_message: str, task_type: str = None) -> str:
        """Call using new multi-provider router."""
        try:
            # Get model from routing config or fallback to default
            model = MODELS.get(agent_name, "claude-sonnet-4-5-20250929")
            temp = TEMPERATURE.get(agent_name, 0.7)

            # Create request
            request = LLMRequest(
                prompt=user_message,
                system_prompt=system_prompt,
                temperature=temp,
                max_tokens=MAX_TOKENS,
                model=model,
                metadata={"agent": agent_name, "task_type": task_type}
            )

            # Route request
            response = self.router.route_request(
                request=request,
                agent_name=agent_name,
                task_type=task_type
            )

            # Log cost
            print(f"  [{agent_name}] Cost: ${response.cost:.4f} | Total: ${self.cost_tracker.current_cost:.2f}")

            return response.content

        except Exception as e:
            print(f"[ERREUR] Agent {agent_name} : {e}")
            return f"[ERREUR API pour {agent_name}: {e}]"

    def _call_legacy(self, agent_name: str, system_prompt: str, user_message: str) -> str:
        """Call using legacy Anthropic-only client."""
        try:
            response = self.client.messages.create(
                model=MODELS.get(agent_name, "claude-sonnet-4-5-20250929"),
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE.get(agent_name, 0.7),
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"[ERREUR] Agent {agent_name} : {e}")
            return f"[ERREUR API pour {agent_name}: {e}]"

    def _simulate(self, agent_name: str, user_message: str) -> str:
        """Return simulated response."""
        simulations = {
            "TIMBO": self._simulate_timbo,
            "ZAT": self._simulate_zat,
            "MARY": self._simulate_mary,
            "RANA": self._simulate_rana,
            "COMPLIANCE_EXTRACTOR": self._simulate_compliance,
        }
        return simulations.get(agent_name, lambda m: "[Agent inconnu]")(user_message)

    def _simulate_timbo(self, brief: str) -> str:
        return """# CAHIER DES CHARGES STRATEGIQUE
## Projet : Analyse du brief recu

### 1. Resume executif
TIMBO a analyse le projet soumis et identifie les axes strategiques principaux.
Le projet presente une faisabilite elevee avec des risques maitrisables.

### 2. Analyse contextuelle
**Chaine de Valeur** : Le projet s'inscrit dans une logique de creation de valeur
sur les activites principales (operations, logistique sortante) et de soutien (technologie).

**SWOT** :
- Forces : Expertise KPLW, positionnement unique
- Faiblesses : Ressources limitees
- Opportunites : Marche en croissance, demande forte
- Menaces : Concurrence des Big 3

**PESTEL** : Environnement favorable, cadre reglementaire stable.

### 3. Evaluation de faisabilite : 78/100
- Complexite : Moyenne (65/100)
- Ressources : Suffisantes (80/100)
- Delai : Realiste (85/100)
- Risques : Maitrisables (82/100)

---
*Analyse TIMBO completee. Transmission a ZAT pour conception.*"""

    def _simulate_zat(self, cahier: str) -> str:
        return """# BLUEPRINT DE SOLUTION
## Conception multi-scenarios

### 1. Analyse du cahier des charges
Cahier des charges de TIMBO recu et analyse. Trois scenarios concus.

### 2. Scenario A : Approche Conservative
- **Description** : Solution eprouvee, risque minimal, implementation rapide
- **Avantages** : Fiable, previsible, cout maitrise
- **Cout estime** : 15 000 - 25 000 CAD
- **Delai** : 4-6 semaines

### 3. Scenario B : Approche Equilibree (RECOMMANDE)
- **Description** : Combinaison innovation et pragmatisme
- **Avantages** : Bon rapport qualite/risque
- **Cout estime** : 25 000 - 40 000 CAD
- **Delai** : 6-8 semaines

---
*Blueprint ZAT complete. Transmission a MARY pour production.*"""

    def _simulate_mary(self, blueprint: str) -> str:
        return """# LIVRABLE PROJET
## Document final

### 1. Executive Summary
Ce document presente la solution proposee par KPLW Strategic Innovations.

### 2. Recommandations strategiques
Nous recommandons une approche equilibree combinant innovation et pragmatisme.

### 3. Plan d'implementation
- Phase 1 : Analyse et conception (2 semaines)
- Phase 2 : Developpement (4 semaines)
- Phase 3 : Tests et deploiement (2 semaines)

---
*Livrable MARY complete. Transmission a RANA pour validation.*"""

    def _simulate_rana(self, livrable: str) -> str:
        return """# EVALUATION RANA
## Score : 82/100

### Forces
- Document bien structure et professionnel
- Recommandations claires et actionnables
- Plan d'implementation detaille

### Points d'amelioration mineurs
- Quelques details techniques pourraient etre approfondis

## DECISION : VALIDE
Le livrable respecte les standards de qualite KPLW et peut etre soumis au client."""

    def _simulate_compliance(self, rfp_text: str) -> str:
        return ""  # Returns empty for simulation mode

    def get_cost_summary(self) -> dict:
        """Get cost tracking summary."""
        if hasattr(self, 'cost_tracker'):
            return {
                'total_cost': self.cost_tracker.current_cost,
                'num_calls': len(self.cost_tracker.calls) if self.cost_tracker.calls else 0,
                'budget_limit': self.cost_tracker.budget_limit,
                'budget_remaining': self.cost_tracker.budget_limit - self.cost_tracker.current_cost if self.cost_tracker.budget_limit else None
            }
        return {'total_cost': 0, 'num_calls': 0}


# ════════════════════════════════════════════════════════════
# BASE AGENT
# ════════════════════════════════════════════════════════════

class BaseAgent:
    """Base agent class for KPLW system."""

    def __init__(self, name: str, system_prompt: str, llm_client: LLMClient):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm_client

    def execute(self, input_text: str, task_type: str = None) -> str:
        """Execute the agent with input text."""
        print(f"\n{'='*60}")
        print(f"  AGENT {self.name} EN COURS D'EXECUTION...")
        print(f"{'='*60}")
        result = self.llm.call(self.name, self.system_prompt, input_text, task_type)
        print(f"  [{self.name}] Execution terminee.")
        return result

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
