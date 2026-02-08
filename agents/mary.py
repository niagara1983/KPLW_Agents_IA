"""
MARY Agent - Content Generation
Responsible for generating professional RFP proposal content
"""

from .base import BaseAgent, LLMClient
from prompts_rfp import MARY_RFP_CONTENT_PROMPT


class MARYAgent(BaseAgent):
    """
    MARY - Proposal Content Writer

    Responsibilities:
    - Compliance-first writing approach
    - Requirement addressing methodology
    - Evidence and proof points integration
    - Professional RFP writing standards
    - Compliance matrix integration
    - Win themes and differentiators
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__("MARY", MARY_RFP_CONTENT_PROMPT, llm_client)

    def generate_proposal(
        self,
        zat_blueprint: str,
        requirements: list = None,
        rfp_text: str = None,
        previous_version: str = None,
        rana_feedback: str = None
    ) -> str:
        """
        Generate or revise proposal content.

        Args:
            zat_blueprint: ZAT's structure blueprint
            requirements: List of requirements to address
            rfp_text: Original RFP text
            previous_version: Previous proposal version (for revision)
            rana_feedback: RANA's feedback (for revision)

        Returns:
            Complete proposal content
        """
        if previous_version and rana_feedback:
            # Revision mode
            mary_input = f"""ZAT BLUEPRINT:
{zat_blueprint}

PREVIOUS PROPOSAL:
{previous_version}

RANA CORRECTIONS:
{rana_feedback}

Revise the proposal according to RANA's feedback."""

        else:
            # Initial generation
            mary_input = f"""ZAT BLUEPRINT:
{zat_blueprint}
"""

            if requirements:
                req_text = self._format_requirements(requirements)
                mary_input += f"\n\nREQUIREMENTS TO ADDRESS:\n{req_text}"

            if rfp_text:
                mary_input += f"\n\nRFP DOCUMENT:\n{rfp_text[:5000]}"  # Truncate for context

            mary_input += "\n\nGenerate the complete RFP response proposal."

        return self.execute(mary_input, task_type="content")

    def _format_requirements(self, requirements: list) -> str:
        """Format requirements for MARY input."""
        lines = ["CRITICAL: Each requirement MUST be addressed explicitly in the proposal:"]

        mandatory = [r for r in requirements if getattr(r, 'is_mandatory', True)]

        for req in mandatory[:30]:  # Limit to 30 most important
            req_id = getattr(req, 'id', 'R???')
            req_text = getattr(req, 'text', str(req))
            lines.append(f"\n{req_id} (MANDATORY): {req_text}")

        return "\n".join(lines)

    def generate_executive_summary(self, proposal: str) -> str:
        """
        Generate executive summary from full proposal.

        Args:
            proposal: Full proposal text

        Returns:
            Executive summary (1-2 pages)
        """
        summary_prompt = f"""Based on this proposal, create a concise executive summary (1-2 pages):

{proposal[:3000]}

The summary should:
- Highlight key value propositions
- Summarize our approach
- State compliance with requirements
- Emphasize differentiators
"""

        return self.llm.call("MARY", self.system_prompt, summary_prompt, task_type="summary")

    def address_specific_requirement(self, requirement: str, context: str = "") -> str:
        """
        Generate response for a specific requirement.

        Args:
            requirement: Requirement text
            context: Additional context

        Returns:
            Detailed response addressing the requirement
        """
        prompt = f"""Requirement: {requirement}

{context}

Provide a detailed, compliance-focused response that:
1. Directly addresses the requirement
2. Provides evidence of capability
3. Includes specific examples or proof points
4. Demonstrates added value
"""

        return self.llm.call("MARY", self.system_prompt, prompt, task_type="requirement")

    def extract_sections(self, proposal: str) -> dict:
        """
        Extract sections from generated proposal.

        Args:
            proposal: Full proposal text

        Returns:
            Dictionary of sections with content
        """
        sections = {}
        current_section = "Introduction"
        current_content = []

        for line in proposal.split('\n'):
            line_stripped = line.strip()

            # Detect section headers (markdown style)
            if line_stripped.startswith('##') and not line_stripped.startswith('###'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)

                # Start new section
                current_section = line_stripped.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def get_word_count(self, proposal: str) -> dict:
        """
        Get word count statistics for proposal.

        Args:
            proposal: Proposal text

        Returns:
            Dictionary with word count stats
        """
        words = proposal.split()
        sections = self.extract_sections(proposal)

        return {
            "total_words": len(words),
            "total_characters": len(proposal),
            "sections": len(sections),
            "avg_words_per_section": len(words) // max(len(sections), 1),
            "estimated_pages": len(words) // 300  # Assuming ~300 words per page
        }
