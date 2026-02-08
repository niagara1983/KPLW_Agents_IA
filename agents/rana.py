"""
RANA Agent - Quality Validation
Responsible for validating proposal quality and compliance
"""

import re
from .base import BaseAgent, LLMClient
from prompts_rfp import RANA_RFP_COMPLIANCE_PROMPT


class RANAAgent(BaseAgent):
    """
    RANA - Quality & Compliance Validator

    Responsibilities:
    - 10-dimension quality evaluation framework
    - Compliance verification
    - Quality scoring (0-100)
    - Gap analysis and feedback
    - Routing decisions (VALIDE / MARY / ZAT / TIMBO)
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__("RANA", RANA_RFP_COMPLIANCE_PROMPT, llm_client)

    def evaluate_proposal(
        self,
        proposal: str,
        timbo_analysis: str = "",
        zat_blueprint: str = "",
        compliance_matrix: str = "",
        rfp_text: str = ""
    ) -> str:
        """
        Evaluate proposal for quality and compliance.

        Args:
            proposal: MARY's proposal content
            timbo_analysis: TIMBO's analysis (reference)
            zat_blueprint: ZAT's blueprint (reference)
            compliance_matrix: Compliance matrix
            rfp_text: Original RFP text

        Returns:
            Complete evaluation with score and decision
        """
        rana_input = f"""PROPOSAL TO EVALUATE:
{proposal}
"""

        if timbo_analysis:
            rana_input += f"\n\nTIMBO ANALYSIS (Reference):\n{timbo_analysis[:2000]}"

        if zat_blueprint:
            rana_input += f"\n\nZAT BLUEPRINT (Reference):\n{zat_blueprint[:2000]}"

        if compliance_matrix:
            rana_input += f"\n\nCOMPLIANCE MATRIX:\n{compliance_matrix}"

        if rfp_text:
            rana_input += f"\n\nRFP ORIGINAL:\n{rfp_text[:3000]}"

        rana_input += "\n\nEvaluate this RFP response for compliance and quality."

        return self.execute(rana_input, task_type="validation")

    def parse_score(self, evaluation: str) -> int:
        """
        Parse RANA score from evaluation text.

        Args:
            evaluation: RANA evaluation output

        Returns:
            Score (0-100)
        """
        # Look for score patterns like "Score: 85/100" or "82/100"
        patterns = [
            r'Score\s*:\s*(\d+)/100',
            r'Score\s*:\s*(\d+)\s*/\s*100',
            r'(\d+)/100',
            r'Score\s*=\s*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, evaluation, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                return min(max(score, 0), 100)  # Clamp to 0-100

        # Default score if not found
        return 75

    def parse_decision(self, evaluation: str) -> str:
        """
        Parse RANA routing decision from evaluation.

        Args:
            evaluation: RANA evaluation output

        Returns:
            Decision: VALIDE, MARY, ZAT, or TIMBO
        """
        # ALWAYS use score-based routing for consistency (ITERATIVE APPROACH)
        # This prevents RANA from accepting low scores as VALIDE
        score = self.parse_score(evaluation)

        if score >= 85:
            return "VALIDE"  # Ready to submit (85+ only)
        elif score >= 50:
            return "MARY"    # Iterative improvement (most common route)
        elif score >= 30:
            return "ZAT"     # Structure redesign needed
        else:
            return "TIMBO"   # Strategic re-analysis (rare)

        # NOTE: We ignore explicit text decisions (e.g., "DECISION: VALIDE") because
        # the LLM sometimes writes VALIDE even with low scores. Score-based routing
        # is more reliable and enforces the 85+ threshold for acceptance.

    def extract_feedback(self, evaluation: str) -> dict:
        """
        Extract structured feedback from evaluation.

        Args:
            evaluation: RANA evaluation output

        Returns:
            Dictionary with strengths, weaknesses, recommendations
        """
        feedback = {
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "critical_issues": []
        }

        lines = evaluation.split('\n')
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()

            # Detect sections
            if "strength" in line_lower or "forces" in line_lower:
                current_section = "strengths"
            elif "weakness" in line_lower or "faiblesse" in line_lower or "amélioration" in line_lower:
                current_section = "weaknesses"
            elif "recommendation" in line_lower or "recommandation" in line_lower:
                current_section = "recommendations"
            elif "critical" in line_lower or "critique" in line_lower:
                current_section = "critical_issues"
            elif line.strip().startswith(('-', '•', '*')) and current_section:
                # Extract bullet point
                item = line.strip().lstrip('-•*').strip()
                if item:
                    feedback[current_section].append(item)

        return feedback

    def calculate_dimension_scores(self, evaluation: str) -> dict:
        """
        Calculate scores for each of the 10 evaluation dimensions.

        Args:
            evaluation: RANA evaluation output

        Returns:
            Dictionary with score per dimension
        """
        dimensions = {
            "compliance_coverage": 0,      # 25%
            "compliance_structure": 0,      # 10%
            "technical_quality": 0,         # 15%
            "clarity": 0,                   # 10%
            "proof_points": 0,              # 10%
            "risk_management": 0,           # 5%
            "pricing_value": 0,             # 5%
            "team_qualifications": 0,       # 5%
            "innovation": 0,                # 10%
            "presentation": 0               # 5%
        }

        # Simple pattern matching - real implementation would parse structured output
        for dimension in dimensions.keys():
            # Look for dimension score in format "Dimension: 8/10" or "85%"
            patterns = [
                rf'{dimension}.*?(\d+)/10',
                rf'{dimension}.*?(\d+)%',
            ]

            for pattern in patterns:
                match = re.search(pattern, evaluation, re.IGNORECASE)
                if match:
                    score = int(match.group(1))
                    # Normalize to 0-100
                    if '/10' in pattern:
                        dimensions[dimension] = score * 10
                    else:
                        dimensions[dimension] = score
                    break

        # If no scores found, estimate based on overall score
        if all(s == 0 for s in dimensions.values()):
            overall = self.parse_score(evaluation)
            for key in dimensions:
                dimensions[key] = overall

        return dimensions

    def get_routing_recommendation(self, score: int, evaluation: str) -> dict:
        """
        Get routing recommendation with reasoning.

        Args:
            score: Overall score
            evaluation: Full evaluation text

        Returns:
            Routing decision with reasoning
        """
        decision = self.parse_decision(evaluation)
        feedback = self.extract_feedback(evaluation)

        reasoning = {
            "VALIDE": "Proposal meets quality standards and is ready for submission",
            "MARY": "Minor content revisions needed to address feedback points",
            "ZAT": "Structural issues require blueprint redesign",
            "TIMBO": "Strategic reorientation needed based on RFP analysis"
        }

        return {
            "decision": decision,
            "score": score,
            "reasoning": reasoning.get(decision, "Review needed"),
            "next_steps": feedback.get("recommendations", []),
            "critical_issues": feedback.get("critical_issues", [])
        }
