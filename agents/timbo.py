"""
TIMBO Agent - Strategic Analysis
Responsible for RFP analysis, requirements identification, and win strategy
"""

from .base import BaseAgent, LLMClient
from prompts_rfp import TIMBO_RFP_ANALYSIS_PROMPT


class TIMBOAgent(BaseAgent):
    """
    TIMBO - Strategic RFP Analyst

    Responsibilities:
    - RFP requirement identification and categorization
    - Evaluation criteria analysis
    - Go/No-Go decision framework
    - Win strategy development
    - Competitive positioning
    - Risk assessment for RFP response
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__("TIMBO", TIMBO_RFP_ANALYSIS_PROMPT, llm_client)

    def analyze_rfp(self, rfp_text: str) -> str:
        """
        Perform complete RFP analysis.

        Args:
            rfp_text: Full RFP document text

        Returns:
            Strategic analysis including requirements, win themes, and recommendations
        """
        return self.execute(rfp_text, task_type="analysis")

    def assess_go_no_go(self, rfp_text: str) -> dict:
        """
        Assess Go/No-Go decision for RFP.

        Args:
            rfp_text: RFP document text

        Returns:
            Dictionary with decision and rationale
        """
        analysis = self.execute(rfp_text, task_type="analysis")

        # Parse analysis for go/no-go indicators
        # This is a simplified version - real implementation would parse the analysis
        decision = {
            "decision": "GO" if "faisabilite elevee" in analysis.lower() or "proceed" in analysis.lower() else "NO-GO",
            "rationale": analysis,
            "confidence": "high" if len(analysis) > 500 else "medium"
        }

        return decision

    def extract_win_themes(self, analysis: str) -> list:
        """
        Extract win themes from TIMBO analysis.

        Args:
            analysis: TIMBO analysis output

        Returns:
            List of win themes
        """
        # Simple extraction - real implementation would use LLM or parsing
        themes = []

        if "differentiation" in analysis.lower():
            themes.append("Unique differentiation")
        if "expertise" in analysis.lower():
            themes.append("Deep expertise")
        if "innovation" in analysis.lower():
            themes.append("Innovative approach")
        if "value" in analysis.lower() or "cost" in analysis.lower():
            themes.append("Value proposition")

        return themes if themes else ["Strategic alignment", "Quality delivery"]

    def identify_risks(self, analysis: str) -> list:
        """
        Identify key risks from TIMBO analysis.

        Args:
            analysis: TIMBO analysis output

        Returns:
            List of identified risks
        """
        # Simple extraction - real implementation would parse risk matrix
        risks = []

        if "deadline" in analysis.lower() or "delai" in analysis.lower():
            risks.append({"risk": "Timeline constraints", "severity": "medium"})
        if "budget" in analysis.lower() or "cout" in analysis.lower():
            risks.append({"risk": "Budget constraints", "severity": "medium"})
        if "complexity" in analysis.lower() or "complexite" in analysis.lower():
            risks.append({"risk": "Technical complexity", "severity": "high"})

        return risks
