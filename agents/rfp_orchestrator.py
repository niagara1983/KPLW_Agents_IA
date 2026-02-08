"""
KPLW RFP Orchestrator
Specialized workflow for RFP response generation
Standalone orchestrator for RFP-specific workflows
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base import BaseAgent as KPLWAgent, LLMClient, ProjectState
from .timbo import TIMBOAgent
from .zat import ZATAgent
from .tess import TESSAgent
from .mary import MARYAgent
from .rana import RANAAgent

from document.parser import DocumentParser
from rfp.compliance import ComplianceExtractor, ComplianceMapper
from rfp.structure import ProposalStructure, get_template
from llm.cost_tracker_file import CostTrackerFile
from prompts_rfp import (
    TIMBO_RFP_ANALYSIS_PROMPT,
    ZAT_RFP_STRUCTURE_PROMPT,
    TESS_CV_ANALYSIS_PROMPT,
    MARY_RFP_CONTENT_PROMPT,
    RANA_RFP_COMPLIANCE_PROMPT
)
from config import MAX_ITERATIONS, QUALITY_THRESHOLD, VISION_ENABLED


class RFPOrchestrator:
    """
    RFP-specific orchestrator for multi-agent workflow.

    Coordinates TIMBO, ZAT, TESS, MARY, and RANA agents for RFP response generation.
    Includes pipeline with compliance matrix, CV analysis, and output formatting.
    """

    def __init__(self):
        """Initialize RFP orchestrator with all agents."""
        # Initialize LLM client
        self.llm = LLMClient()

        # Initialize agents with RFP-specific prompts
        self.timbo = TIMBOAgent(self.llm)
        self.zat = ZATAgent(self.llm)
        self.tess = TESSAgent(self.llm)
        self.mary = MARYAgent(self.llm)
        self.rana = RANAAgent(self.llm)

        # RFP-specific components
        self.document_parser = DocumentParser(
            use_vision=VISION_ENABLED,
            vision_provider=self.llm.provider if hasattr(self.llm, 'provider') else None
        )
        self.compliance_extractor = ComplianceExtractor(self.llm)
        self.compliance_mapper = ComplianceMapper(self.llm)

        # Create RFP-specific agent instances
        self.timbo_rfp = KPLWAgent("TIMBO", TIMBO_RFP_ANALYSIS_PROMPT, self.llm)
        self.zat_rfp = KPLWAgent("ZAT", ZAT_RFP_STRUCTURE_PROMPT, self.llm)
        self.tess_rfp = KPLWAgent("TESS", TESS_CV_ANALYSIS_PROMPT, self.llm)
        self.mary_rfp = KPLWAgent("MARY", MARY_RFP_CONTENT_PROMPT, self.llm)
        self.rana_rfp = KPLWAgent("RANA", RANA_RFP_COMPLIANCE_PROMPT, self.llm)

        # Cost tracking with file persistence
        self.cost_tracker_file = CostTrackerFile("costs_history.json")

    def run_rfp(
        self,
        rfp_files: List[str],
        template_name: str = "government_canada",
        output_formats: List[str] = ["md"],
        team_cvs: Optional[List[str]] = None
    ) -> Dict:
        """
        Execute complete RFP response workflow.

        Args:
            rfp_files: List of RFP document paths (PDF, DOCX, MD)
            template_name: Proposal template to use
            output_formats: Output formats (md, docx, pdf)
            team_cvs: Optional list of team member CV/resume files (PDF, DOCX)

        Returns:
            State dictionary with all outputs
        """
        print("\n" + "=" * 60)
        print("  KPLW RFP RESPONSE GENERATOR")
        print("  Powered by Multi-Agent AI")
        print("=" * 60)
        print(f"\n  RFP Documents: {len(rfp_files)}")
        print(f"  Template: {template_name}")
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Initialize state
        state = {
            "project_id": f"RFP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "rfp_files": rfp_files,
            "template_name": template_name,
            "output_formats": output_formats,
            "started_at": datetime.now().isoformat(),
            "iteration_count": 0,
            "workflow_log": [],
            "status": "en_cours"
        }

        try:
            # ═══════════════════════════════════════════════════════════
            # STAGE 1: Document Parsing & Vision Processing
            # ═══════════════════════════════════════════════════════════
            state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 1: Document parsing")

            print("\n" + "=" * 60)
            print("  STAGE 1: Document Parsing")
            print("=" * 60)

            parsed_docs = self.document_parser.parse_batch(rfp_files)
            state["parsed_documents"] = [doc.to_brief_text() for doc in parsed_docs]
            state["rfp_text"] = "\n\n".join(state["parsed_documents"])

            print(f"  Parsed {len(parsed_docs)} document(s)")
            print(f"  Total text: {len(state['rfp_text'])} characters")

            # ═══════════════════════════════════════════════════════════
            # STAGE 2: Requirement Extraction & Compliance Setup
            # ═══════════════════════════════════════════════════════════
            state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 2: Requirement extraction")

            print("\n" + "=" * 60)
            print("  STAGE 2: Requirement Extraction")
            print("=" * 60)

            requirements = self.compliance_extractor.extract_requirements(state["rfp_text"])
            state["requirements"] = requirements
            state["requirements_count"] = len(requirements)

            mandatory_count = sum(1 for r in requirements if r.is_mandatory)
            print(f"  Extracted {len(requirements)} requirements")
            print(f"  - Mandatory: {mandatory_count}")
            print(f"  - Optional: {len(requirements) - mandatory_count}")

            # ═══════════════════════════════════════════════════════════
            # STAGE 3: TIMBO - RFP Analysis
            # ═══════════════════════════════════════════════════════════
            state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 3: TIMBO RFP analysis")

            timbo_input = f"""RFP DOCUMENT(S):
{state['rfp_text']}

REQUIREMENTS EXTRACTED:
{self._format_requirements_for_timbo(requirements)}

Analyze this RFP and produce the complete strategic analysis."""

            state["timbo_analysis"] = self.timbo_rfp.execute(timbo_input)
            state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] TIMBO: Analysis complete")

            # ═══════════════════════════════════════════════════════════
            # STAGE 4: ZAT - Proposal Structure Design
            # ═══════════════════════════════════════════════════════════
            state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 4: ZAT proposal structure")

            zat_input = f"""TIMBO ANALYSIS:
{state['timbo_analysis']}

RFP REQUIREMENTS:
{self._format_requirements_for_zat(requirements)}

TEMPLATE REQUESTED: {template_name}

Design the complete proposal structure and compliance mapping."""

            state["zat_blueprint"] = self.zat_rfp.execute(zat_input)
            state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] ZAT: Blueprint complete")

            # ═══════════════════════════════════════════════════════════
            # STAGE 4.5: TESS - Team CV Analysis (Optional)
            # ═══════════════════════════════════════════════════════════
            if team_cvs:
                state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 4.5: TESS CV analysis")
                print(f"\n  [TESS] Analyzing {len(team_cvs)} team member CV(s)...")

                # Parse CV files
                cv_data = []
                for cv_file in team_cvs:
                    print(f"    • Parsing: {os.path.basename(cv_file)}")
                    try:
                        cv_text = self.document_parser.parse(cv_file)
                        cv_data.append({
                            'name': os.path.basename(cv_file).replace('.pdf', '').replace('.docx', ''),
                            'content': cv_text
                        })
                    except Exception as e:
                        print(f"      ⚠ Warning: Could not parse {cv_file}: {e}")
                        continue

                if cv_data:
                    # Run TESS analysis
                    tess_input = self.tess.analyze_team_cvs(
                        cv_texts=cv_data,
                        rfp_requirements=self._format_requirements_for_tess(requirements),
                        evaluation_criteria=state.get('timbo_analysis', '')[:2000]
                    )

                    state["tess_team_profiles"] = tess_input
                    state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] TESS: Team profiles generated")

                    # Parse team summary for logging
                    team_summary = self.tess.parse_team_summary(tess_input)
                    print(f"  [TESS] Team Score: {team_summary['team_score']}/10")
                    print(f"  [TESS] Team Members: {team_summary['team_count']}")
                    if team_summary['gaps']:
                        print(f"  [TESS] ⚠ Gaps identified: {len(team_summary['gaps'])}")
                else:
                    print(f"  [TESS] ⚠ No CVs successfully parsed")
                    state["tess_team_profiles"] = None
            else:
                state["tess_team_profiles"] = None
                print(f"  [TESS] Skipped - No team CVs provided")

            # ═══════════════════════════════════════════════════════════
            # STAGE 5: MARY Production + RANA Validation Loop
            # ═══════════════════════════════════════════════════════════
            validated = False
            while state["iteration_count"] < MAX_ITERATIONS and not validated:
                state["iteration_count"] += 1
                print(f"\n  --- Iteration {state['iteration_count']}/{MAX_ITERATIONS} ---")

                # MARY: Generate proposal content
                state["workflow_log"].append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 5: MARY content generation (iteration {state['iteration_count']})"
                )

                if state["iteration_count"] == 1:
                    # Build MARY input for first iteration
                    mary_input = f"""ZAT BLUEPRINT:
{state['zat_blueprint']}

REQUIREMENTS TO ADDRESS:
{self._format_requirements_for_mary(requirements)}

RFP DOCUMENT:
{state['rfp_text'][:5000]}  # Truncate for context
"""
                    # Add team profiles if available
                    if state.get("tess_team_profiles"):
                        mary_input += f"""

TEAM PROFILES (from TESS):
{state['tess_team_profiles'][:6000]}  # Truncate if needed

IMPORTANT: Integrate these tailored team profiles into the appropriate sections
of the proposal (Team Composition, Key Personnel, etc.). Use EXACTLY the profiles
provided by TESS - they are already tailored to this RFP.
"""

                    mary_input += "\n\nGenerate the complete RFP response proposal."
                else:
                    # Build MARY input for revisions
                    mary_input = f"""ZAT BLUEPRINT:
{state['zat_blueprint']}

PREVIOUS PROPOSAL:
{state['mary_deliverable']}

RANA CORRECTIONS:
{state['rana_evaluation']}
"""
                    # Add team profiles if available
                    if state.get("tess_team_profiles"):
                        mary_input += f"""

TEAM PROFILES (from TESS - reference if needed):
{state['tess_team_profiles'][:4000]}
"""

                    mary_input += "\n\nRevise the proposal according to RANA's feedback."

                state["mary_deliverable"] = self.mary_rfp.execute(mary_input)
                state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] MARY: Proposal generated")

                # ═══════════════════════════════════════════════════════════
                # STAGE 6: Compliance Matrix Generation
                # ═══════════════════════════════════════════════════════════
                state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 6: Compliance mapping")

                # Extract sections from MARY's output
                proposal_sections = self._extract_sections(state["mary_deliverable"])

                # Map requirements to sections
                compliance_matrix = self.compliance_mapper.map_proposal_to_requirements(
                    requirements=requirements,
                    proposal_sections=proposal_sections
                )

                state["compliance_matrix"] = compliance_matrix.to_markdown()
                state["compliance_score"] = compliance_matrix.compliance_score
                state["compliance_gaps"] = compliance_matrix.get_gaps()

                print(f"  Compliance Score: {state['compliance_score']:.1f}%")

                # ═══════════════════════════════════════════════════════════
                # STAGE 7: RANA - Quality & Compliance Validation
                # ═══════════════════════════════════════════════════════════
                state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 7: RANA validation")

                rana_input = f"""PROPOSAL TO EVALUATE:
{state['mary_deliverable']}

TIMBO ANALYSIS (Reference):
{state['timbo_analysis']}

ZAT BLUEPRINT (Reference):
{state['zat_blueprint']}

COMPLIANCE MATRIX:
{state['compliance_matrix']}

RFP ORIGINAL:
{state['rfp_text'][:3000]}

Evaluate this RFP response for compliance and quality."""

                state["rana_evaluation"] = self.rana_rfp.execute(rana_input)

                # Parse RANA score and decision
                score, decision = self._parse_rana_output(state["rana_evaluation"])
                state["rana_score"] = score
                state["rana_decision"] = decision

                print(f"\n  RANA Score: {score}/100 | Decision: {decision}")
                state["workflow_log"].append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] RANA: score {score}/100 -> {decision}"
                )

                # Check validation
                if decision == "VALIDE" or score >= QUALITY_THRESHOLD:
                    validated = True
                    state["status"] = "valide"
                    print(f"\n  ✓ Proposal VALIDATED (Score: {score}/100, Compliance: {state['compliance_score']:.1f}%)")
                elif decision == "ZAT":
                    # Reconception needed
                    state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Routing: ZAT reconception")
                    zat_input = f"""RANA EVALUATION (Redesign required):
{state['rana_evaluation']}

PREVIOUS BLUEPRINT:
{state['zat_blueprint']}

Redesign the proposal structure based on RANA's feedback."""
                    state["zat_blueprint"] = self.zat_rfp.execute(zat_input)
                elif decision == "TIMBO":
                    # Strategic reorientation
                    state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Routing: TIMBO reorientation")
                    timbo_input = f"""RANA EVALUATION (Reorientation required):
{state['rana_evaluation']}

PREVIOUS ANALYSIS:
{state['timbo_analysis']}

Re-evaluate the RFP analysis strategy."""
                    state["timbo_analysis"] = self.timbo_rfp.execute(timbo_input)
                    # Re-run ZAT with new analysis
                    zat_input = f"New TIMBO analysis:\n{state['timbo_analysis']}\n\nRedesign blueprint."
                    state["zat_blueprint"] = self.zat_rfp.execute(zat_input)

            # Finalization
            if not validated:
                state["status"] = "escalade_humaine"
                print(f"\n  ⚠ Maximum iterations reached. Human escalation required.")

            state["completed_at"] = datetime.now().isoformat()

            # Add cost summary if available
            if hasattr(self.llm, 'get_cost_summary'):
                state["cost_summary"] = self.llm.get_cost_summary()

                # Save costs to persistent file
                rfp_name = os.path.basename(rfp_files[0]) if rfp_files else "Unknown"
                self.cost_tracker_file.add_run(
                    project_id=state.get("project_id", "Unknown"),
                    rfp_name=rfp_name,
                    cost_summary=state["cost_summary"],
                    agent_costs={},  # TODO: Track per-agent costs
                    metadata={
                        "template": template_name,
                        "iterations": state.get("iteration_count", 0),
                        "rana_score": state.get("rana_score", 0),
                        "compliance_score": state.get("compliance_score", 0),
                        "status": state.get("status", "unknown")
                    }
                )

            # Print final summary
            self._print_rfp_summary(state)

            # ═══════════════════════════════════════════════════════════
            # STAGE 8: Output Generation (DOCX/PDF)
            # ═══════════════════════════════════════════════════════════
            if "docx" in output_formats or "pdf" in output_formats or "all" in output_formats:
                state["workflow_log"].append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 8: Output generation")
                state["generated_files"] = self._generate_outputs(state, template_name, output_formats)

            return state

        except Exception as e:
            print(f"\n  [ERROR] RFP workflow failed: {e}")
            import traceback
            traceback.print_exc()
            state["status"] = "erreur"
            state["error"] = str(e)
            return state

    def _format_requirements_for_timbo(self, requirements) -> str:
        """Format requirements for TIMBO input."""
        lines = []
        for req in requirements[:50]:  # Limit to first 50 for context
            lines.append(f"- [{req.id}] {req.text} (Priority: {req.priority}, Mandatory: {req.is_mandatory})")
        return "\n".join(lines)

    def _format_requirements_for_zat(self, requirements) -> str:
        """Format requirements for ZAT input."""
        lines = ["Requirements to address in proposal:"]
        for req in requirements:
            lines.append(f"  {req.id}: {req.text}")
            lines.append(f"    Category: {req.category.value}, Priority: {req.priority}")
        return "\n".join(lines)

    def _format_requirements_for_mary(self, requirements) -> str:
        """Format requirements for MARY input."""
        lines = ["CRITICAL: Each requirement MUST be addressed explicitly in the proposal:"]
        mandatory = [r for r in requirements if r.is_mandatory]
        for req in mandatory:
            lines.append(f"\n{req.id} (MANDATORY): {req.text}")
        return "\n".join(lines)

    def _format_requirements_for_tess(self, requirements) -> str:
        """Format requirements for TESS CV analysis."""
        lines = ["RFP Requirements (focus on team/qualifications-related):"]

        # Focus on requirements related to team, experience, qualifications
        team_related_keywords = ['team', 'personnel', 'experience', 'qualification',
                                 'certification', 'expertise', 'skills', 'cv', 'resume',
                                 'équipe', 'expérience', 'compétence', 'certification']

        team_reqs = []
        other_reqs = []

        for req in requirements:
            req_lower = req.text.lower()
            if any(keyword in req_lower for keyword in team_related_keywords):
                team_reqs.append(req)
            else:
                other_reqs.append(req)

        # List team-related requirements first
        if team_reqs:
            lines.append("\n** TEAM-RELATED REQUIREMENTS (HIGH PRIORITY FOR CV MATCHING):")
            for req in team_reqs:
                lines.append(f"  {req.id}: {req.text}")
                lines.append(f"    Priority: {req.priority}, Mandatory: {req.is_mandatory}")

        # Then other requirements (for context)
        if other_reqs[:10]:  # Limit to first 10 other requirements
            lines.append("\n** OTHER REQUIREMENTS (for context):")
            for req in other_reqs[:10]:
                lines.append(f"  {req.id}: {req.text}")

        return "\n".join(lines)

    def _extract_sections(self, proposal_text: str) -> Dict[str, str]:
        """Extract sections from MARY's proposal for compliance mapping."""
        sections = {}
        current_section = "Introduction"
        current_content = []

        for line in proposal_text.split('\n'):
            # Detect section headers (markdown style)
            if line.startswith('##') and not line.startswith('###'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)

                # Start new section
                current_section = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _parse_rana_output(self, evaluation: str) -> tuple:
        """
        Parse RANA score and decision from evaluation text.

        Returns:
            (score, decision) tuple
        """
        score = self.rana.parse_score(evaluation)
        decision = self.rana.parse_decision(evaluation)
        return score, decision

    def _save_markdown_outputs(self, state: Dict, output_dir: str, project_id: str):
        """Save individual agent outputs as markdown files."""
        # TIMBO analysis
        if state.get("timbo_analysis"):
            path = os.path.join(output_dir, f"{project_id}_1_TIMBO_analyse.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# Analyse TIMBO\n## Projet : {project_id}\n\n")
                f.write(state["timbo_analysis"])

        # ZAT blueprint
        if state.get("zat_blueprint"):
            path = os.path.join(output_dir, f"{project_id}_2_ZAT_blueprint.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# Blueprint ZAT\n## Projet : {project_id}\n\n")
                f.write(state["zat_blueprint"])

        # MARY deliverable
        if state.get("mary_deliverable"):
            path = os.path.join(output_dir, f"{project_id}_3_MARY_livrable.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# Livrable MARY\n## Projet : {project_id}\n\n")
                f.write(state["mary_deliverable"])

        # RANA evaluation
        if state.get("rana_evaluation"):
            path = os.path.join(output_dir, f"{project_id}_4_RANA_evaluation.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# Evaluation RANA\n## Projet : {project_id}\n\n")
                f.write(state["rana_evaluation"])

        # Compliance matrix
        if state.get("compliance_matrix"):
            path = os.path.join(output_dir, f"{project_id}_COMPLIANCE_MATRIX.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(state["compliance_matrix"])

    def _print_rfp_summary(self, state: Dict):
        """Print RFP workflow summary."""
        print("\n" + "=" * 60)
        print("  RFP WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"  Project: {state['project_id']}")
        print(f"  Status: {state['status'].upper()}")
        print(f"  Quality Score: {state.get('rana_score', 'N/A')}/100")
        print(f"  Compliance: {state.get('compliance_score', 'N/A'):.1f}%")
        print(f"  Iterations: {state['iteration_count']}")

        # Compliance gaps
        gaps = state.get("compliance_gaps", [])
        if gaps:
            print(f"\n  ⚠ Compliance Gaps: {len(gaps)} requirements not fully addressed")
            for gap in gaps[:5]:  # Show first 5
                print(f"    - {gap.id}: {gap.text[:60]}...")

        # Cost summary
        if state.get("cost_summary"):
            cost = state["cost_summary"]
            print(f"\n  Cost: ${cost.get('total_cost', 0):.2f}")
            print(f"  API Calls: {cost.get('num_calls', 0)}")

        print("=" * 60)

        if state["status"] == "valide":
            print("\n  ✓ RFP RESPONSE READY FOR SUBMISSION")
        else:
            print("\n  ⚠ ATTENTION: Manual review required")

        print("=" * 60)

    def _generate_outputs(
        self,
        state: Dict,
        template_name: str,
        output_formats: List[str]
    ) -> Dict[str, str]:
        """
        Generate DOCX and PDF outputs from workflow state.

        Args:
            state: RFP workflow state
            template_name: Template name used
            output_formats: List of formats to generate

        Returns:
            Dictionary mapping format to file path
        """
        generated = {}
        project_id = state.get("project_id", "RFP-unknown")
        output_dir = "outputs"

        print("\n" + "=" * 60)
        print("  STAGE 8: Output Generation")
        print("=" * 60)

        try:
            # ALWAYS generate markdown files for internal review
            print(f"  [MD] Generating agent output files...")
            self._save_markdown_outputs(state, output_dir, project_id)
            generated["markdown"] = f"{project_id}_*.md"
            print(f"  [MD] ✓ Generated: Individual agent markdown files")

            # Generate DOCX
            if "docx" in output_formats or "all" in output_formats:
                from rfp.generators.docx_generator import DOCXGenerator

                docx_path = os.path.join(output_dir, f"{project_id}_PROPOSAL.docx")
                print(f"  [DOCX] Generating clean proposal document...")

                generator = DOCXGenerator()
                # include_internal=False → Only MARY's proposal (client-ready)
                generator.generate(state, docx_path, template_name, include_internal=False)

                generated["docx"] = docx_path
                print(f"  [DOCX] ✓ Generated: {docx_path} (client-ready, MARY only)")

            # Generate PDF
            if "pdf" in output_formats or "all" in output_formats:
                try:
                    from rfp.generators.pdf_generator import PDFGenerator

                    pdf_generator = PDFGenerator()

                    if not pdf_generator.is_available():
                        print(f"  [PDF] ⚠ PDF generation not available")
                        print(f"        Install: pip install docx2pdf")
                        print(f"        Or: brew install libreoffice")
                    else:
                        pdf_path = os.path.join(output_dir, f"{project_id}_PROPOSAL.pdf")

                        # If we generated DOCX, convert it
                        if "docx" in generated:
                            print(f"  [PDF] Converting DOCX to PDF...")
                            pdf_generator.generate_from_docx(generated["docx"], pdf_path)
                            generated["pdf"] = pdf_path
                        else:
                            # Generate from markdown
                            md_path = os.path.join(output_dir, f"{project_id}_RAPPORT_COMPLET.md")
                            if os.path.exists(md_path):
                                print(f"  [PDF] Converting Markdown to PDF...")
                                pdf_generator.generate_from_markdown(md_path, pdf_path)
                                generated["pdf"] = pdf_path

                except Exception as e:
                    print(f"  [PDF] ⚠ PDF generation failed: {e}")
                    print(f"        Continuing with other formats...")
                    # Don't crash - PDF is optional, continue with other formats

        except Exception as e:
            print(f"  [ERROR] Output generation failed: {e}")
            import traceback
            traceback.print_exc()

        print("=" * 60)

        return generated
