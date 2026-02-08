"""
TESS Agent - Team Expertise Selection Specialist
Analyzes CVs and extracts relevant experience for RFP proposals
"""

from typing import Dict, List, Optional
from .base import BaseAgent
from prompts_rfp import TESS_CV_ANALYSIS_PROMPT
import re


class TESSAgent(BaseAgent):
    """
    TESS (Team Expertise Selection Specialist)
    Analyzes team CVs against RFP requirements and generates tailored team profiles.
    """

    def __init__(self, llm_client):
        """Initialize TESS agent."""
        super().__init__(
            name="TESS",
            role="Team Expertise Selection Specialist",
            llm_client=llm_client,
            system_prompt=TESS_CV_ANALYSIS_PROMPT
        )

    def analyze_team_cvs(
        self,
        cv_texts: List[Dict[str, str]],
        rfp_requirements: str,
        evaluation_criteria: str = ""
    ) -> str:
        """
        Analyze team CVs against RFP requirements.

        Args:
            cv_texts: List of dicts with 'name' and 'content' keys
            rfp_requirements: RFP requirements text (from TIMBO)
            evaluation_criteria: Evaluation criteria from RFP (optional)

        Returns:
            Tailored team profiles as markdown
        """
        # Build analysis prompt
        cv_section = "\n\n".join([
            f"### CV: {cv['name']}\n{cv['content'][:4000]}"  # Limit each CV
            for cv in cv_texts
        ])

        user_message = f"""RFP REQUIREMENTS:
{rfp_requirements[:3000]}

EVALUATION CRITERIA (Team-related):
{evaluation_criteria[:2000] if evaluation_criteria else "Non spécifié"}

---

TEAM CVs TO ANALYZE:
{cv_section}

---

Analyse chaque CV et génère des profils d'équipe ciblés pour ce RFP.
Inclus UNIQUEMENT l'expérience pertinente (score ≥ 6/10).
Fais le mapping explicite : expérience → requirements RFP.
"""

        result = self.execute(user_message, task_type="analysis")
        return result

    def parse_team_summary(self, tess_output: str) -> Dict:
        """
        Parse TESS output to extract team summary.

        Args:
            tess_output: Full TESS analysis output

        Returns:
            Dictionary with team_score, gaps, coverage
        """
        summary = {
            'team_score': 0,
            'gaps': [],
            'coverage': {},
            'team_count': 0
        }

        # Extract team score
        score_match = re.search(r'Score global de l\'équipe.*?(\d+)/10', tess_output, re.IGNORECASE)
        if score_match:
            summary['team_score'] = int(score_match.group(1))

        # Extract gaps
        gaps_section = re.search(
            r'Gaps identifiés\s*:\s*(.+?)(?:\n\n|---|\Z)',
            tess_output,
            re.DOTALL | re.IGNORECASE
        )
        if gaps_section:
            gaps_text = gaps_section.group(1).strip()
            if "aucun" not in gaps_text.lower():
                # Parse individual gaps
                gap_lines = [line.strip() for line in gaps_text.split('\n') if line.strip()]
                summary['gaps'] = gap_lines

        # Count team members
        team_count = len(re.findall(r'^###\s+[A-Z]', tess_output, re.MULTILINE))
        summary['team_count'] = team_count

        return summary

    def extract_team_profiles(self, tess_output: str) -> List[Dict[str, str]]:
        """
        Extract individual team member profiles from TESS output.

        Args:
            tess_output: Full TESS analysis

        Returns:
            List of profile dictionaries with name, role, profile_text
        """
        profiles = []

        # Split by individual profiles (### Name, Title pattern)
        profile_sections = re.split(r'^(###\s+.+?)$', tess_output, flags=re.MULTILINE)

        for i in range(1, len(profile_sections), 2):
            if i + 1 < len(profile_sections):
                header = profile_sections[i].strip()
                content = profile_sections[i + 1].strip()

                # Extract name from header
                name_match = re.search(r'###\s+([^,]+)', header)
                if name_match:
                    name = name_match.group(1).strip()

                    # Extract role
                    role_match = re.search(
                        r'\*\*Rôle proposé.*?\*\*\s*:\s*(.+?)(?:\n|$)',
                        content,
                        re.IGNORECASE
                    )
                    role = role_match.group(1).strip() if role_match else "Non spécifié"

                    profiles.append({
                        'name': name,
                        'role': role,
                        'profile_text': header + '\n\n' + content
                    })

        return profiles
