#!/usr/bin/env python3
"""
Phase 2 Test Script
Test RFP-specific functionality: compliance extraction, proposal structure, RFP workflow
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_compliance_extractor():
    """Test requirement extraction from RFP text."""
    print("\n" + "=" * 60)
    print("TEST 1: Compliance Extractor")
    print("=" * 60)

    from rfp.compliance import Requirement, RequirementCategory
    from agents import LLMClient

    # Test creating requirements manually
    req1 = Requirement(
        id="R001",
        text="The vendor must have ISO 27001 certification",
        category=RequirementCategory.MANDATORY,
        priority=1,
        is_mandatory=True
    )

    req2 = Requirement(
        id="R002",
        text="Experience with government projects is preferred",
        category=RequirementCategory.OPTIONAL,
        priority=4,
        is_mandatory=False
    )

    print(f"✓ Created test requirements")
    print(f"  - {req1.id}: {req1.text[:50]}... (Mandatory: {req1.is_mandatory})")
    print(f"  - {req2.id}: {req2.text[:50]}... (Mandatory: {req2.is_mandatory})")


def test_compliance_matrix():
    """Test compliance matrix generation."""
    print("\n" + "=" * 60)
    print("TEST 2: Compliance Matrix")
    print("=" * 60)

    from rfp.compliance import (
        Requirement, RequirementMapping, ComplianceMatrix,
        RequirementCategory, ComplianceStatus
    )

    # Create test requirements
    requirements = [
        Requirement(
            id="R001",
            text="Must provide 24/7 support",
            category=RequirementCategory.MANDATORY,
            is_mandatory=True
        ),
        Requirement(
            id="R002",
            text="Should include mobile app",
            category=RequirementCategory.OPTIONAL,
            is_mandatory=False
        ),
    ]

    # Create test mappings
    mappings = [
        RequirementMapping(
            requirement=requirements[0],
            proposal_section="Support Services",
            compliance_status=ComplianceStatus.FULLY_COMPLIANT,
            response_text="We provide 24/7 support with dedicated team.",
            section_reference="Section 5.2",
            confidence=0.95
        ),
        RequirementMapping(
            requirement=requirements[1],
            proposal_section="Technical Solution",
            compliance_status=ComplianceStatus.PARTIALLY_COMPLIANT,
            response_text="Mobile app in development, available Q2 2026.",
            section_reference="Section 3.4",
            confidence=0.70
        ),
    ]

    # Create matrix
    matrix = ComplianceMatrix(requirements=requirements, mappings=mappings)

    print(f"✓ Compliance matrix created")
    print(f"  - Total requirements: {len(requirements)}")
    print(f"  - Mappings: {len(mappings)}")
    print(f"  - Compliance score: {matrix.compliance_score:.1f}%")
    print(f"  - Fully compliant: {matrix.is_fully_compliant()}")

    # Generate markdown
    md = matrix.to_markdown()
    print(f"  - Markdown generated: {len(md)} characters")


def test_proposal_structure():
    """Test proposal structure templates."""
    print("\n" + "=" * 60)
    print("TEST 3: Proposal Structure Templates")
    print("=" * 60)

    from rfp.structure import get_template, list_templates

    # List available templates
    templates = list_templates()
    print(f"✓ Available templates: {len(templates)}")
    for template_name in templates:
        print(f"  - {template_name}")

    # Get a specific template
    template = get_template("government_canada")
    if template:
        print(f"\n✓ Loaded template: {template.template_name}")
        print(f"  - Sections: {len(template.sections)}")
        print(f"  - Required sections: {len(template.get_required_sections())}")

        # Show first 3 sections
        for section in template.sections[:3]:
            print(f"    {section.order}. {section.name} (Required: {section.required})")
    else:
        print("✗ Failed to load template")


def test_rfp_prompts():
    """Test RFP-specific prompts are loaded."""
    print("\n" + "=" * 60)
    print("TEST 4: RFP Prompts")
    print("=" * 60)

    try:
        from prompts_rfp import (
            TIMBO_RFP_ANALYSIS_PROMPT,
            ZAT_RFP_STRUCTURE_PROMPT,
            MARY_RFP_CONTENT_PROMPT,
            RANA_RFP_COMPLIANCE_PROMPT
        )

        print(f"✓ TIMBO RFP prompt loaded: {len(TIMBO_RFP_ANALYSIS_PROMPT)} characters")
        print(f"✓ ZAT RFP prompt loaded: {len(ZAT_RFP_STRUCTURE_PROMPT)} characters")
        print(f"✓ MARY RFP prompt loaded: {len(MARY_RFP_CONTENT_PROMPT)} characters")
        print(f"✓ RANA RFP prompt loaded: {len(RANA_RFP_COMPLIANCE_PROMPT)} characters")

    except Exception as e:
        print(f"✗ Failed to load RFP prompts: {e}")


def test_rfp_orchestrator():
    """Test RFP orchestrator initialization."""
    print("\n" + "=" * 60)
    print("TEST 5: RFP Orchestrator")
    print("=" * 60)

    try:
        from agents.rfp_orchestrator import RFPOrchestrator

        orchestrator = RFPOrchestrator()

        print(f"✓ RFP orchestrator initialized")
        print(f"  - Has document parser: {hasattr(orchestrator, 'document_parser')}")
        print(f"  - Has compliance extractor: {hasattr(orchestrator, 'compliance_extractor')}")
        print(f"  - Has compliance mapper: {hasattr(orchestrator, 'compliance_mapper')}")
        print(f"  - Has RFP agents: {hasattr(orchestrator, 'timbo_rfp')}")

    except Exception as e:
        print(f"✗ Failed to initialize RFP orchestrator: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all Phase 2 tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  KPLW Phase 2 Test Suite".center(58) + "║")
    print("║" + "  RFP Core Logic & Compliance".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    test_compliance_extractor()
    test_compliance_matrix()
    test_proposal_structure()
    test_rfp_prompts()
    test_rfp_orchestrator()

    print("\n" + "=" * 60)
    print("Phase 2 Testing Complete")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test with real RFP: python main.py --rfp --rfp-files rfp.md")
    print("2. Verify compliance matrix generation")
    print("3. Check proposal structure compliance")
    print()


if __name__ == "__main__":
    main()
