"""
ZAT Agent - Proposal Structure Design
Responsible for designing proposal structure and compliance mapping
"""

from .base import BaseAgent, LLMClient
from prompts_rfp import ZAT_RFP_STRUCTURE_PROMPT


class ZATAgent(BaseAgent):
    """
    ZAT - Proposal Structure Architect

    Responsibilities:
    - Template selection logic
    - Compliance-first structure design
    - Section-to-requirement mapping
    - Page limit optimization
    - Visual aids planning (charts, tables)
    - RFP-specific formatting requirements
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__("ZAT", ZAT_RFP_STRUCTURE_PROMPT, llm_client)

    def design_structure(self, timbo_analysis: str, requirements: list = None, template_name: str = "government_canada") -> str:
        """
        Design proposal structure based on TIMBO analysis.

        Args:
            timbo_analysis: TIMBO's strategic analysis
            requirements: List of RFP requirements (optional)
            template_name: Template to use

        Returns:
            Complete proposal structure blueprint
        """
        # Build input for ZAT
        zat_input = f"""TIMBO ANALYSIS:
{timbo_analysis}

TEMPLATE REQUESTED: {template_name}
"""

        if requirements:
            req_text = "\n".join([f"- {getattr(r, 'text', str(r))}" for r in requirements[:20]])
            zat_input += f"\n\nRFP REQUIREMENTS:\n{req_text}"

        zat_input += "\n\nDesign the complete proposal structure and compliance mapping."

        return self.execute(zat_input, task_type="structure")

    def map_requirements_to_sections(self, requirements: list, blueprint: str) -> dict:
        """
        Map requirements to proposal sections.

        Args:
            requirements: List of requirements
            blueprint: ZAT blueprint

        Returns:
            Dictionary mapping sections to requirements
        """
        # Simplified mapping - real implementation would use LLM parsing
        mapping = {}

        # Extract sections from blueprint
        sections = []
        for line in blueprint.split('\n'):
            if line.startswith('###') and not line.startswith('####'):
                section = line.strip('#').strip()
                sections.append(section)

        # Simple mapping logic
        for i, req in enumerate(requirements[:len(sections)]):
            section = sections[i % len(sections)] if sections else f"Section {i+1}"
            if section not in mapping:
                mapping[section] = []
            mapping[section].append(getattr(req, 'id', f'R{i+1}'))

        return mapping

    def validate_structure(self, blueprint: str, template_name: str) -> dict:
        """
        Validate proposal structure against template requirements.

        Args:
            blueprint: ZAT blueprint
            template_name: Template being used

        Returns:
            Validation results with missing sections
        """
        # Load template requirements
        from rfp.structure import get_template

        template = get_template(template_name)

        if not template:
            return {"valid": False, "error": "Template not found"}

        # Extract sections from blueprint
        blueprint_sections = []
        for line in blueprint.split('\n'):
            if line.startswith('##') and not line.startswith('###'):
                section = line.strip('#').strip()
                blueprint_sections.append(section)

        # Check required sections
        required_sections = [s.name for s in template.get_required_sections()]
        missing = [s for s in required_sections if s not in blueprint_sections]

        return {
            "valid": len(missing) == 0,
            "blueprint_sections": blueprint_sections,
            "required_sections": required_sections,
            "missing_sections": missing,
            "template": template_name
        }

    def optimize_page_allocation(self, blueprint: str, total_pages: int = 50) -> dict:
        """
        Optimize page allocation across sections.

        Args:
            blueprint: ZAT blueprint
            total_pages: Total page limit

        Returns:
            Page allocation per section
        """
        # Extract sections
        sections = []
        for line in blueprint.split('\n'):
            if line.startswith('##') and not line.startswith('###'):
                sections.append(line.strip('#').strip())

        if not sections:
            return {}

        # Simple allocation - distribute evenly
        pages_per_section = total_pages // len(sections)
        remainder = total_pages % len(sections)

        allocation = {}
        for i, section in enumerate(sections):
            # Give extra pages to first sections
            allocation[section] = pages_per_section + (1 if i < remainder else 0)

        return allocation
