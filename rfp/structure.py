"""
Proposal Structure Templates
Configurable templates for different types of RFP responses
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ProposalSection:
    """Defines a section in a proposal."""
    name: str
    required: bool = True
    max_pages: Optional[int] = None
    description: str = ""
    order: int = 0


@dataclass
class ProposalStructure:
    """Defines the complete structure of a proposal."""
    template_name: str
    sections: List[ProposalSection]
    formatting: Dict[str, str] = field(default_factory=dict)
    instructions: str = ""

    def get_section_names(self) -> List[str]:
        """Get list of section names in order."""
        return [s.name for s in sorted(self.sections, key=lambda x: x.order)]

    def get_required_sections(self) -> List[ProposalSection]:
        """Get only required sections."""
        return [s for s in self.sections if s.required]

    def validate_proposal(self, sections_present: List[str]) -> tuple[bool, List[str]]:
        """
        Validate that proposal has all required sections.

        Returns:
            (is_valid, missing_sections)
        """
        required_names = {s.name for s in self.get_required_sections()}
        present_names = set(sections_present)
        missing = list(required_names - present_names)

        return (len(missing) == 0, missing)


# ═══════════════════════════════════════════════════════════════════
# PREDEFINED PROPOSAL TEMPLATES
# ═══════════════════════════════════════════════════════════════════

PROPOSAL_TEMPLATES = {
    "government_canada": ProposalStructure(
        template_name="Government of Canada RFP",
        sections=[
            ProposalSection(
                name="Cover Letter",
                required=True,
                max_pages=1,
                description="Formal letter introducing the proposal",
                order=1
            ),
            ProposalSection(
                name="Executive Summary",
                required=True,
                max_pages=2,
                description="High-level overview of the proposal",
                order=2
            ),
            ProposalSection(
                name="Understanding of Requirements",
                required=True,
                description="Demonstrate comprehension of RFP requirements",
                order=3
            ),
            ProposalSection(
                name="Technical Approach",
                required=True,
                description="Detailed technical solution and methodology",
                order=4
            ),
            ProposalSection(
                name="Team Experience and Qualifications",
                required=True,
                description="Team members, roles, and relevant experience",
                order=5
            ),
            ProposalSection(
                name="Project Management Approach",
                required=True,
                description="How the project will be managed",
                order=6
            ),
            ProposalSection(
                name="Budget and Pricing",
                required=True,
                description="Detailed cost breakdown",
                order=7
            ),
            ProposalSection(
                name="Schedule and Timeline",
                required=True,
                description="Project timeline with milestones",
                order=8
            ),
            ProposalSection(
                name="Risk Management",
                required=True,
                description="Identified risks and mitigation strategies",
                order=9
            ),
            ProposalSection(
                name="References",
                required=True,
                description="Client references for similar projects",
                order=10
            ),
            ProposalSection(
                name="Compliance Matrix",
                required=True,
                description="Requirement-by-requirement compliance",
                order=11
            ),
            ProposalSection(
                name="Appendices",
                required=False,
                description="Supporting documents and certifications",
                order=12
            ),
        ],
        formatting={
            "font": "Arial",
            "font_size": "11pt",
            "line_spacing": "1.15",
            "margins": "1 inch all sides",
            "page_numbers": "Bottom center",
            "header": "Company name and RFP number"
        },
        instructions="""
        Follow Treasury Board of Canada guidelines for proposal format.
        All pages must be numbered. Use clear headings and subheadings.
        Include table of contents. Comply with page limits where specified.
        """
    ),

    "corporate": ProposalStructure(
        template_name="Corporate RFP",
        sections=[
            ProposalSection(
                name="Executive Summary",
                required=True,
                max_pages=2,
                description="Concise overview for executives",
                order=1
            ),
            ProposalSection(
                name="Company Overview",
                required=True,
                description="Company background and capabilities",
                order=2
            ),
            ProposalSection(
                name="Proposed Solution",
                required=True,
                description="Detailed solution addressing RFP requirements",
                order=3
            ),
            ProposalSection(
                name="Implementation Plan",
                required=True,
                description="Step-by-step implementation approach",
                order=4
            ),
            ProposalSection(
                name="Team and Resources",
                required=True,
                description="Team structure and resource allocation",
                order=5
            ),
            ProposalSection(
                name="Pricing",
                required=True,
                description="Cost structure and pricing model",
                order=6
            ),
            ProposalSection(
                name="Timeline",
                required=True,
                description="Project schedule and key milestones",
                order=7
            ),
            ProposalSection(
                name="Case Studies",
                required=False,
                description="Relevant success stories",
                order=8
            ),
            ProposalSection(
                name="Terms and Conditions",
                required=True,
                description="Legal terms and contract structure",
                order=9
            ),
            ProposalSection(
                name="Compliance Matrix",
                required=True,
                description="Requirement compliance checklist",
                order=10
            ),
        ],
        formatting={
            "font": "Calibri or Arial",
            "font_size": "11pt",
            "line_spacing": "Single",
            "margins": "1 inch",
            "branding": "Include company logo and colors"
        },
        instructions="""
        Professional business format. Use compelling language.
        Highlight differentiators and competitive advantages.
        Include relevant graphics and charts.
        """
    ),

    "consulting": ProposalStructure(
        template_name="Consulting Services RFP",
        sections=[
            ProposalSection(
                name="Executive Summary",
                required=True,
                max_pages=1,
                description="Strategic overview and key recommendations",
                order=1
            ),
            ProposalSection(
                name="Situation Analysis",
                required=True,
                description="Current state assessment and challenges",
                order=2
            ),
            ProposalSection(
                name="Approach and Methodology",
                required=True,
                description="Consulting methodology and frameworks",
                order=3
            ),
            ProposalSection(
                name="Scope of Work",
                required=True,
                description="Detailed deliverables and activities",
                order=4
            ),
            ProposalSection(
                name="Team Composition",
                required=True,
                description="Consultant bios and expertise",
                order=5
            ),
            ProposalSection(
                name="Work Plan and Timeline",
                required=True,
                description="Phased approach with milestones",
                order=6
            ),
            ProposalSection(
                name="Investment",
                required=True,
                description="Fee structure and payment terms",
                order=7
            ),
            ProposalSection(
                name="Expected Outcomes",
                required=True,
                description="Success metrics and value proposition",
                order=8
            ),
            ProposalSection(
                name="Relevant Experience",
                required=True,
                description="Case studies and client testimonials",
                order=9
            ),
            ProposalSection(
                name="Assumptions and Exclusions",
                required=True,
                description="Scope boundaries and dependencies",
                order=10
            ),
        ],
        formatting={
            "font": "Times New Roman or Garamond",
            "font_size": "11-12pt",
            "line_spacing": "1.5",
            "style": "Professional consulting firm style",
            "emphasis": "Data-driven insights and frameworks"
        },
        instructions="""
        Use consulting best practices (McKinsey, BCG, Bain style).
        Include frameworks, matrices, and strategic insights.
        Emphasize thought leadership and expertise.
        Quantify impact and ROI where possible.
        """
    ),

    "international_development": ProposalStructure(
        template_name="International Development RFP",
        sections=[
            ProposalSection(
                name="Executive Summary",
                required=True,
                max_pages=3,
                description="Proposal overview in English and French",
                order=1
            ),
            ProposalSection(
                name="Context Analysis",
                required=True,
                description="Country/regional context and needs assessment",
                order=2
            ),
            ProposalSection(
                name="Technical Approach",
                required=True,
                description="Development methodology and interventions",
                order=3
            ),
            ProposalSection(
                name="Logical Framework",
                required=True,
                description="Logframe with outputs, outcomes, indicators",
                order=4
            ),
            ProposalSection(
                name="Stakeholder Engagement",
                required=True,
                description="Consultation and participation strategy",
                order=5
            ),
            ProposalSection(
                name="Sustainability Plan",
                required=True,
                description="Long-term sustainability and exit strategy",
                order=6
            ),
            ProposalSection(
                name="Monitoring and Evaluation",
                required=True,
                description="M&E framework and data collection",
                order=7
            ),
            ProposalSection(
                name="Team Expertise",
                required=True,
                description="International and local team members",
                order=8
            ),
            ProposalSection(
                name="Budget",
                required=True,
                description="Detailed budget with unit costs",
                order=9
            ),
            ProposalSection(
                name="Risk Management",
                required=True,
                description="Political, security, and operational risks",
                order=10
            ),
            ProposalSection(
                name="Gender Equality and Social Inclusion",
                required=True,
                description="GESI mainstreaming approach",
                order=11
            ),
            ProposalSection(
                name="Past Performance",
                required=True,
                description="Similar projects and results achieved",
                order=12
            ),
        ],
        formatting={
            "font": "Arial",
            "font_size": "11pt",
            "line_spacing": "Single",
            "bilingual": "Sections may require English and French",
            "annexes": "Extensive appendices expected"
        },
        instructions="""
        Follow DAC (Development Assistance Committee) standards.
        Include logframe/results framework. Demonstrate development impact.
        Address cross-cutting themes (gender, environment, governance).
        Comply with donor regulations (CIDA, DFID, EU, World Bank, etc.).
        """
    ),

    "it_services": ProposalStructure(
        template_name="IT Services RFP",
        sections=[
            ProposalSection(
                name="Executive Summary",
                required=True,
                max_pages=2,
                order=1
            ),
            ProposalSection(
                name="Technical Solution",
                required=True,
                description="Architecture, technology stack, and design",
                order=2
            ),
            ProposalSection(
                name="System Requirements",
                required=True,
                description="Functional and non-functional requirements",
                order=3
            ),
            ProposalSection(
                name="Implementation Methodology",
                required=True,
                description="Agile/Waterfall approach and delivery phases",
                order=4
            ),
            ProposalSection(
                name="Security and Compliance",
                required=True,
                description="Security measures, data protection, compliance",
                order=5
            ),
            ProposalSection(
                name="Testing and Quality Assurance",
                required=True,
                description="Testing strategy and quality gates",
                order=6
            ),
            ProposalSection(
                name="Team and Roles",
                required=True,
                description="Development team structure and expertise",
                order=7
            ),
            ProposalSection(
                name="Project Timeline",
                required=True,
                description="Gantt chart with sprints and milestones",
                order=8
            ),
            ProposalSection(
                name="Pricing Model",
                required=True,
                description="Fixed price, T&M, or hybrid pricing",
                order=9
            ),
            ProposalSection(
                name="Support and Maintenance",
                required=True,
                description="Post-launch support and SLAs",
                order=10
            ),
            ProposalSection(
                name="Change Management",
                required=False,
                description="User training and adoption strategy",
                order=11
            ),
            ProposalSection(
                name="Technical Compliance Matrix",
                required=True,
                description="Requirement-by-requirement technical compliance",
                order=12
            ),
        ],
        formatting={
            "font": "Arial or Helvetica",
            "font_size": "10-11pt",
            "diagrams": "Technical diagrams and architecture drawings",
            "code_samples": "Include relevant code examples if applicable"
        },
        instructions="""
        Use technical detail appropriate for IT audience.
        Include architecture diagrams, data flows, ERDs.
        Demonstrate technical expertise and best practices.
        Address scalability, performance, security.
        """
    ),
}


def get_template(template_name: str) -> Optional[ProposalStructure]:
    """Get proposal template by name."""
    return PROPOSAL_TEMPLATES.get(template_name)


def list_templates() -> List[str]:
    """List available template names."""
    return list(PROPOSAL_TEMPLATES.keys())


def create_custom_template(
    name: str,
    sections: List[ProposalSection],
    **kwargs
) -> ProposalStructure:
    """Create a custom proposal template."""
    return ProposalStructure(
        template_name=name,
        sections=sections,
        **kwargs
    )


@dataclass
class TemplateMetadata:
    """Metadata for template selection in UI."""
    name: str  # Internal ID (e.g., "government_canada")
    display_name: str  # French display name
    description: str  # French description


def get_all_templates() -> List[TemplateMetadata]:
    """Get all available templates with French metadata for UI."""
    return [
        TemplateMetadata(
            name="government_canada",
            display_name="Gouvernement du Canada",
            description="Modèle pour les appels d'offres du gouvernement canadien (fédéral et provincial)"
        ),
        TemplateMetadata(
            name="corporate",
            display_name="RFP Corporatif",
            description="Modèle pour les propositions d'entreprises privées"
        ),
        TemplateMetadata(
            name="consulting",
            display_name="Services de Conseil",
            description="Modèle pour les services de conseil stratégique et consulting"
        ),
        TemplateMetadata(
            name="international_development",
            display_name="Développement International",
            description="Modèle pour les projets de développement international et coopération"
        ),
        TemplateMetadata(
            name="it_services",
            display_name="Services TI",
            description="Modèle pour les services informatiques et développement logiciel"
        ),
    ]
