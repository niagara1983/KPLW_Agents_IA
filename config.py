"""
KPLW Strategic Innovations - Configuration du Systeme Multi-Agents v2.0
========================================================================
Charge les parametres depuis .env (via python-dotenv) avec valeurs par defaut.
"""

import os
from pathlib import Path

# ── Charger .env si present ──
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv optionnel, on utilise les valeurs par defaut

# ══════════════════════════════════════
# CLE API ANTHROPIC
# ══════════════════════════════════════
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ══════════════════════════════════════
# MODELES LLM PAR AGENT
# ══════════════════════════════════════
# Recommandation production :
#   TIMBO & RANA → claude-opus-4-5-20251101 (raisonnement profond)
#   ZAT & MARY  → claude-sonnet-4-5-20250929 (vitesse + qualite)
MODELS = {
    "TIMBO": os.getenv("MODEL_TIMBO", "claude-sonnet-4-5-20250929"),
    "ZAT":   os.getenv("MODEL_ZAT",   "claude-sonnet-4-5-20250929"),
    "MARY":  os.getenv("MODEL_MARY",  "claude-sonnet-4-5-20250929"),
    "RANA":  os.getenv("MODEL_RANA",   "claude-sonnet-4-5-20250929"),
}

# ══════════════════════════════════════
# TEMPERATURES DIFFERENCIEES
# ══════════════════════════════════════
# TIMBO (0.3) : analyse rigoureuse, peu de variance
# ZAT (0.5)   : creativite moderee pour les scenarios
# MARY (0.4)  : production equilibree
# RANA (0.2)   : evaluation deterministe
TEMPERATURE = {
    "TIMBO": float(os.getenv("TEMP_TIMBO", "0.3")),
    "ZAT":   float(os.getenv("TEMP_ZAT",   "0.5")),
    "MARY":  float(os.getenv("TEMP_MARY",  "0.4")),
    "RANA":  float(os.getenv("TEMP_RANA",   "0.2")),
}

# ══════════════════════════════════════
# PARAMETRES DU WORKFLOW
# ══════════════════════════════════════
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
QUALITY_THRESHOLD = int(os.getenv("QUALITY_THRESHOLD", "80"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))

# ══════════════════════════════════════
# MODE SIMULATION
# ══════════════════════════════════════
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() == "true"

# ══════════════════════════════════════
# RETRY & RESILIENCE
# ══════════════════════════════════════
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))  # secondes, doublee a chaque retry

# ══════════════════════════════════════
# SUIVI DES COUTS (USD par million de tokens)
# ══════════════════════════════════════
# Tarifs Anthropic (mis a jour : fevrier 2026)
COST_PER_1M_INPUT = {
    "claude-sonnet-4-5-20250929": 3.0,
    "claude-opus-4-5-20251101": 15.0,
    "claude-haiku-4-5-20251001": 0.80,
}
COST_PER_1M_OUTPUT = {
    "claude-sonnet-4-5-20250929": 15.0,
    "claude-opus-4-5-20251101": 75.0,
    "claude-haiku-4-5-20251001": 4.0,
}

# ══════════════════════════════════════
# MULTI-PROVIDER CONFIGURATION (NEW)
# ══════════════════════════════════════
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "anthropic")  # anthropic, openai, azure, ollama

# Provider API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Vision Model Configuration
VISION_ENABLED = os.getenv("VISION_ENABLED", "true").lower() == "true"
VISION_MODEL_ANTHROPIC = os.getenv("VISION_MODEL_ANTHROPIC", "claude-opus-4-5-20251101")
VISION_MODEL_OPENAI = os.getenv("VISION_MODEL_OPENAI", "gpt-4o")

# Task-Based Model Routing
MODEL_ROUTING = {
    "TIMBO": {
        "analysis": os.getenv("TIMBO_ANALYSIS_MODEL", "claude-opus-4-5-20251101"),
        "extraction": os.getenv("TIMBO_EXTRACTION_MODEL", "claude-sonnet-4-5-20250929"),
    },
    "ZAT": {
        "scenario_design": os.getenv("ZAT_SCENARIO_MODEL", "claude-sonnet-4-5-20250929"),
        "financial": os.getenv("ZAT_FINANCIAL_MODEL", "claude-opus-4-5-20251101"),
    },
    "MARY": {
        "narrative": os.getenv("MARY_NARRATIVE_MODEL", "claude-sonnet-4-5-20250929"),
        "compliance": os.getenv("MARY_COMPLIANCE_MODEL", "claude-haiku-4-5-20251001"),
        "tables": os.getenv("MARY_TABLES_MODEL", "claude-haiku-4-5-20251001"),
    },
    "RANA": {
        "evaluation": os.getenv("RANA_EVALUATION_MODEL", "claude-opus-4-5-20251101"),
    }
}

# Budget Controls
BUDGET_LIMIT_USD = float(os.getenv("BUDGET_LIMIT_USD", "100.0"))  # Max cost per run
COST_ALERT_THRESHOLD = float(os.getenv("COST_ALERT_THRESHOLD", "0.75"))  # Alert at 75%
ENABLE_COST_APPROVAL = os.getenv("ENABLE_COST_APPROVAL", "false").lower() == "true"

# ══════════════════════════════════════
# SORTIE
# ══════════════════════════════════════
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "md")  # md, docx, ou les deux
