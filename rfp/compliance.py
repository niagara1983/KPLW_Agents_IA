"""
Compliance Matrix Generator
Extract requirements from RFPs and map proposal responses to them
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import re


class RequirementCategory(Enum):
    """Categories of RFP requirements."""
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    EVALUATION_CRITERIA = "evaluation_criteria"
    DELIVERABLE = "deliverable"
    TECHNICAL = "technical"
    BUSINESS = "business"
    OTHER = "other"


class ComplianceStatus(Enum):
    """Compliance status for each requirement."""
    FULLY_COMPLIANT = "fully_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_ADDRESSED = "not_addressed"


@dataclass
class Requirement:
    """Represents a single RFP requirement."""
    id: str
    text: str
    category: RequirementCategory
    priority: int = 3  # 1=critical, 2=high, 3=medium, 4=low, 5=optional
    section_reference: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    is_mandatory: bool = True

    def matches_keywords(self, text: str) -> bool:
        """Check if text contains requirement keywords."""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)


@dataclass
class RequirementMapping:
    """Maps a requirement to proposal response."""
    requirement: Requirement
    proposal_section: str
    compliance_status: ComplianceStatus
    response_text: str
    section_reference: str
    confidence: float = 1.0  # 0.0-1.0
    notes: str = ""

    def is_compliant(self) -> bool:
        """Check if requirement is fully compliant."""
        return self.compliance_status == ComplianceStatus.FULLY_COMPLIANT


@dataclass
class ComplianceMatrix:
    """Complete compliance matrix for an RFP response."""
    requirements: List[Requirement]
    mappings: List[RequirementMapping] = field(default_factory=list)

    @property
    def compliance_score(self) -> float:
        """Calculate overall compliance percentage."""
        if not self.requirements:
            return 0.0

        mandatory_reqs = [r for r in self.requirements if r.is_mandatory]
        if not mandatory_reqs:
            return 100.0

        compliant_mandatory = sum(
            1 for m in self.mappings
            if m.requirement.is_mandatory and m.is_compliant()
        )

        return (compliant_mandatory / len(mandatory_reqs)) * 100

    def get_gaps(self) -> List[Requirement]:
        """Get requirements that are not fully addressed."""
        mapped_req_ids = {m.requirement.id for m in self.mappings if m.is_compliant()}
        return [r for r in self.requirements if r.id not in mapped_req_ids]

    def is_fully_compliant(self) -> bool:
        """Check if all mandatory requirements are met."""
        return self.compliance_score == 100.0

    def to_markdown(self) -> str:
        """Generate markdown table of compliance matrix."""
        lines = [
            "# Compliance Matrix",
            "",
            f"**Overall Compliance**: {self.compliance_score:.1f}%",
            "",
            "| Req ID | Category | Requirement | Status | Proposal Section | Reference |",
            "|--------|----------|-------------|--------|------------------|-----------|"
        ]

        for mapping in self.mappings:
            req = mapping.requirement
            status_icon = {
                ComplianceStatus.FULLY_COMPLIANT: "✓",
                ComplianceStatus.PARTIALLY_COMPLIANT: "◐",
                ComplianceStatus.NON_COMPLIANT: "✗",
                ComplianceStatus.NOT_ADDRESSED: "○"
            }.get(mapping.compliance_status, "?")

            lines.append(
                f"| {req.id} | {req.category.value} | {req.text[:50]}... | "
                f"{status_icon} {mapping.compliance_status.value} | "
                f"{mapping.proposal_section} | {mapping.section_reference} |"
            )

        # Add gaps
        gaps = self.get_gaps()
        if gaps:
            lines.extend([
                "",
                "## Gaps (Not Addressed)",
                "",
                "| Req ID | Category | Requirement |",
                "|--------|----------|-------------|"
            ])
            for req in gaps:
                lines.append(f"| {req.id} | {req.category.value} | {req.text[:80]}... |")

        return "\n".join(lines)


class ComplianceExtractor:
    """Extract requirements from RFP documents using LLM."""

    def __init__(self, llm_client):
        """
        Initialize extractor.

        Args:
            llm_client: LLMClient instance for making LLM calls
        """
        self.llm_client = llm_client

    def extract_requirements(self, rfp_text: str) -> List[Requirement]:
        """
        Extract structured requirements from RFP text.

        Args:
            rfp_text: Full text of RFP document(s)

        Returns:
            List of Requirement objects
        """
        # Use LLM to identify requirements
        prompt = self._build_extraction_prompt(rfp_text)

        response = self.llm_client.call(
            agent_name="COMPLIANCE_EXTRACTOR",
            system_prompt=self._get_system_prompt(),
            user_message=prompt,
            task_type="extraction"
        )

        # Parse LLM response into requirements
        requirements = self._parse_requirements(response)

        # Categorize and prioritize
        requirements = self._categorize_requirements(requirements)

        # Filter out administrative/submission requirements
        requirements = self._filter_administrative_requirements(requirements)

        return requirements

    def _build_extraction_prompt(self, rfp_text: str) -> str:
        """Build prompt for requirement extraction."""
        return f"""Analyze this RFP document and extract ALL requirements.

For each requirement, provide:
1. A unique ID (R001, R002, etc.)
2. The exact requirement text
3. Whether it's mandatory or optional
4. The category (mandatory, optional, deliverable, technical, business, evaluation_criteria)
5. Priority level (1=critical, 2=high, 3=medium, 4=low, 5=optional)
6. Section reference from the RFP

Format each requirement as:
ID: R###
TEXT: [requirement text]
MANDATORY: yes/no
CATEGORY: [category]
PRIORITY: [1-5]
SECTION: [section reference]
---

RFP DOCUMENT:
{rfp_text[:8000]}  # Truncate if too long

Extract ALL requirements now:"""

    def _get_system_prompt(self) -> str:
        """Get system prompt for extractor."""
        return """You are an expert at analyzing RFP documents and extracting PROPOSAL CONTENT requirements.

Your task is to identify requirements that relate to THE PROPOSAL CONTENT ITSELF, including:
- Mandatory content requirements (MUST, SHALL, REQUIRED)
- Optional content requirements (SHOULD, MAY, OPTIONAL)
- Deliverables and outputs (what the proposal must describe/provide)
- Technical specifications and capabilities required
- Business qualifications and experience to demonstrate
- Evaluation criteria (topics/areas proposals will be scored on)

IMPORTANT - EXCLUDE these administrative/submission items:
- Submission instructions (how/where to submit, email addresses, upload portals)
- Deadline and date requirements (when to submit)
- Contact information and communication procedures
- Document format specifications (PDF, Word, page limits)
- Administrative procedural steps (registration, forms, signatures)

ONLY extract requirements that describe WHAT THE PROPOSAL MUST CONTAIN OR ADDRESS.
Do NOT extract requirements about HOW/WHERE/WHEN to submit the proposal.

Be thorough and precise. Extract content requirements exactly as stated in the RFP."""

    def _parse_requirements(self, llm_response: str) -> List[Requirement]:
        """Parse LLM response into Requirement objects."""
        requirements = []
        current_req = {}

        for line in llm_response.split('\n'):
            line = line.strip()

            if line.startswith('ID:'):
                if current_req:
                    requirements.append(self._build_requirement(current_req))
                current_req = {'id': line[3:].strip()}

            elif line.startswith('TEXT:'):
                current_req['text'] = line[5:].strip()

            elif line.startswith('MANDATORY:'):
                current_req['mandatory'] = 'yes' in line.lower()

            elif line.startswith('CATEGORY:'):
                category_text = line[9:].strip().lower()
                current_req['category'] = category_text

            elif line.startswith('PRIORITY:'):
                try:
                    current_req['priority'] = int(line[9:].strip()[0])
                except:
                    current_req['priority'] = 3

            elif line.startswith('SECTION:'):
                current_req['section'] = line[8:].strip()

        # Add last requirement
        if current_req:
            requirements.append(self._build_requirement(current_req))

        return requirements

    def _build_requirement(self, req_dict: Dict) -> Requirement:
        """Build Requirement object from parsed data."""
        category_map = {
            'mandatory': RequirementCategory.MANDATORY,
            'optional': RequirementCategory.OPTIONAL,
            'deliverable': RequirementCategory.DELIVERABLE,
            'technical': RequirementCategory.TECHNICAL,
            'business': RequirementCategory.BUSINESS,
            'evaluation_criteria': RequirementCategory.EVALUATION_CRITERIA,
        }

        category = category_map.get(
            req_dict.get('category', 'other'),
            RequirementCategory.OTHER
        )

        # Extract keywords from requirement text
        keywords = self._extract_keywords(req_dict.get('text', ''))

        return Requirement(
            id=req_dict.get('id', 'R000'),
            text=req_dict.get('text', ''),
            category=category,
            priority=req_dict.get('priority', 3),
            section_reference=req_dict.get('section'),
            keywords=keywords,
            is_mandatory=req_dict.get('mandatory', True)
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from requirement text."""
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b', text)
        return list(set(words[:5]))  # Top 5 unique capitalized terms

    def _categorize_requirements(self, requirements: List[Requirement]) -> List[Requirement]:
        """Apply additional categorization logic."""
        for req in requirements:
            # Detect mandatory keywords
            mandatory_keywords = ['must', 'shall', 'required', 'mandatory']
            optional_keywords = ['should', 'may', 'optional', 'recommended']

            text_lower = req.text.lower()

            if any(kw in text_lower for kw in mandatory_keywords):
                req.is_mandatory = True
                if req.priority > 2:
                    req.priority = 2  # Upgrade priority

            elif any(kw in text_lower for kw in optional_keywords):
                req.is_mandatory = False
                if req.priority < 4:
                    req.priority = 4  # Downgrade priority

        return requirements

    def _filter_administrative_requirements(self, requirements: List[Requirement]) -> List[Requirement]:
        """
        Filter out administrative/submission requirements.
        Only keep requirements related to proposal content.
        """
        # Administrative patterns to exclude
        administrative_patterns = [
            # Submission methods
            r'transmi[st].*par.*courriel',  # transmis/transmises par courriel
            r'send.*by.*email',
            r'submit.*via.*email',
            r'upload.*to.*portal',
            r'deliver.*to.*address',

            # Deadline/timing
            r'\bdate\b.*limit',
            r'deadline',
            r'before.*\d{4}',  # dates
            r'no later than',
            r'au plus tard',

            # Contact/communication
            r'contact.*for.*question',
            r'adresse.*courriel',
            r'email address',
            r'phone number',
            r'contacter.*pour',

            # Document format (not content)
            r'format.*pdf',
            r'page limit',
            r'font size',
            r'margin',
            r'document format',

            # Administrative procedures
            r'registration.*required',
            r'signature.*required',
            r'form.*attached',
            r'certificat.*requis',  # unless about technical/business capability
        ]

        filtered = []
        for req in requirements:
            text_lower = req.text.lower()

            # Check if requirement matches any administrative pattern
            is_administrative = any(
                re.search(pattern, text_lower)
                for pattern in administrative_patterns
            )

            # Additional heuristics
            # If requirement is ONLY about submission/contact, exclude it
            submission_keywords = ['transmi', 'submit', 'send', 'email', 'courriel',
                                  'contact', 'adresse', 'upload']
            content_keywords = ['proposal', 'proposition', 'demonstrate', 'describe',
                               'provide', 'include', 'address', 'explain']

            has_submission_only = (
                any(kw in text_lower for kw in submission_keywords) and
                not any(kw in text_lower for kw in content_keywords)
            )

            # Keep if it's NOT administrative
            if not is_administrative and not has_submission_only:
                filtered.append(req)
            else:
                # Log filtered requirements for debugging
                print(f"  [COMPLIANCE] Filtered administrative req: {req.id} - {req.text[:60]}...")

        return filtered


class ComplianceMapper:
    """Map proposal content to RFP requirements."""

    def __init__(self, llm_client):
        """
        Initialize mapper.

        Args:
            llm_client: LLMClient instance for making LLM calls
        """
        self.llm_client = llm_client

    def map_proposal_to_requirements(
        self,
        requirements: List[Requirement],
        proposal_sections: Dict[str, str]
    ) -> ComplianceMatrix:
        """
        Map proposal sections to requirements.

        Args:
            requirements: List of extracted requirements
            proposal_sections: Dict of section_name -> content

        Returns:
            ComplianceMatrix with mappings
        """
        matrix = ComplianceMatrix(requirements=requirements)

        # For each requirement, find matching proposal section
        for req in requirements:
            mapping = self._find_mapping(req, proposal_sections)
            if mapping:
                matrix.mappings.append(mapping)

        return matrix

    def _find_mapping(
        self,
        requirement: Requirement,
        proposal_sections: Dict[str, str]
    ) -> Optional[RequirementMapping]:
        """Find where requirement is addressed in proposal."""
        best_match = None
        best_score = 0.0

        for section_name, content in proposal_sections.items():
            # Simple keyword matching (could use LLM for better matching)
            score = self._calculate_match_score(requirement, content)

            if score > best_score:
                best_score = score
                best_match = (section_name, content)

        if best_match and best_score > 0.3:  # Threshold
            section_name, content = best_match

            # Determine compliance status
            status = self._assess_compliance(requirement, content, best_score)

            # Extract relevant excerpt
            excerpt = self._extract_relevant_text(requirement, content)

            return RequirementMapping(
                requirement=requirement,
                proposal_section=section_name,
                compliance_status=status,
                response_text=excerpt,
                section_reference=section_name,
                confidence=best_score
            )

        # No match found
        return RequirementMapping(
            requirement=requirement,
            proposal_section="N/A",
            compliance_status=ComplianceStatus.NOT_ADDRESSED,
            response_text="",
            section_reference="N/A",
            confidence=0.0,
            notes="Requirement not addressed in proposal"
        )

    def _calculate_match_score(self, requirement: Requirement, content: str) -> float:
        """Calculate how well content addresses requirement."""
        score = 0.0

        # Keyword matching
        if requirement.matches_keywords(content):
            score += 0.5

        # Exact text matching
        req_words = set(requirement.text.lower().split())
        content_words = set(content.lower().split())
        overlap = len(req_words & content_words)
        score += (overlap / len(req_words)) * 0.5 if req_words else 0.0

        return min(score, 1.0)

    def _assess_compliance(
        self,
        requirement: Requirement,
        content: str,
        match_score: float
    ) -> ComplianceStatus:
        """Assess compliance level based on match quality."""
        if match_score > 0.8:
            return ComplianceStatus.FULLY_COMPLIANT
        elif match_score > 0.5:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        elif match_score > 0.3:
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.NOT_ADDRESSED

    def _extract_relevant_text(self, requirement: Requirement, content: str, max_length: int = 200) -> str:
        """Extract most relevant excerpt from content."""
        # Find sentences containing keywords
        sentences = content.split('.')
        relevant = []

        for sentence in sentences:
            if requirement.matches_keywords(sentence):
                relevant.append(sentence.strip())

        if relevant:
            excerpt = '. '.join(relevant[:2])  # First 2 relevant sentences
            if len(excerpt) > max_length:
                excerpt = excerpt[:max_length] + "..."
            return excerpt

        # Fallback: return first part of content
        return content[:max_length] + "..." if len(content) > max_length else content
