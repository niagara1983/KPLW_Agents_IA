"""
KPLW Multi-Agent System
Professional RFP Response Generation

Agents:
- TIMBO: Strategic RFP Analysis
- ZAT: Proposal Structure Design
- TESS: Team Expertise Selection (CV Analysis)
- MARY: Content Generation
- RANA: Quality & Compliance Validation

Orchestrator:
- RFPOrchestrator: RFP-specific workflow (imported separately from agents.rfp_orchestrator)
"""

# Base classes
from .base import (
    ProjectState,
    LLMClient,
    BaseAgent
)

# Individual agents
from .timbo import TIMBOAgent
from .zat import ZATAgent
from .tess import TESSAgent
from .mary import MARYAgent
from .rana import RANAAgent

# Legacy compatibility - keep old class name
KPLWAgent = BaseAgent


__all__ = [
    # Base classes
    'ProjectState',
    'LLMClient',
    'BaseAgent',
    'KPLWAgent',  # Legacy alias

    # Agents
    'TIMBOAgent',
    'ZATAgent',
    'TESSAgent',
    'MARYAgent',
    'RANAAgent',
]

__version__ = '2.0.0'
