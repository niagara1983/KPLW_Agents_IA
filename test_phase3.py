#!/usr/bin/env python3
"""
Phase 3 Test Script
Test DOCX and PDF generation capabilities
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_docx_generator():
    """Test DOCX generator."""
    print("\n" + "=" * 60)
    print("TEST 1: DOCX Generator")
    print("=" * 60)

    try:
        from rfp.generators.docx_generator import DOCXGenerator, DocumentStyle

        # Create mock state
        state = {
            "project_id": "TEST-RFP-001",
            "status": "valide",
            "rana_score": 85,
            "compliance_score": 92.5,
            "requirements_count": 15,
            "iteration_count": 2,
            "timbo_analysis": """# TIMBO Strategic Analysis

## Executive Summary
This is a test analysis conducted by TIMBO agent.

## Key Findings
- Strategic alignment identified
- Risk assessment completed
- Win strategy developed

## Recommendations
1. Proceed with proposal
2. Focus on differentiators
3. Address compliance gaps
""",
            "zat_blueprint": """# ZAT Proposal Blueprint

## Structure Design
- Template: Government of Canada
- Sections: 11 required sections
- Page limits: Adhered to all limits

## Compliance Mapping
All requirements mapped to appropriate sections.
""",
            "mary_deliverable": """# MARY Proposal Content

## Executive Summary
This proposal presents our comprehensive solution.

## Technical Approach
### Architecture
Our solution leverages modern architecture patterns.

### Implementation
- Phase 1: Design
- Phase 2: Development
- Phase 3: Testing

## Team Qualifications
Our team has 10+ years experience.
""",
            "rana_evaluation": """# RANA Quality Evaluation

## Overall Score: 85/100

### Strengths
- Strong technical approach
- Comprehensive compliance
- Professional presentation

### Areas for Improvement
- Minor formatting issues
- Some sections could be expanded

## Recommendation: VALIDE
""",
            "compliance_matrix": "# Compliance Matrix\n\nAll requirements addressed.",
            "requirements": [],
            "compliance_gaps": []
        }

        # Create custom style
        style = DocumentStyle(
            company_name="KPLW Strategic Innovations Inc.",
            font_name="Arial",
            color_primary=(0, 51, 102)
        )

        # Generate DOCX
        generator = DOCXGenerator(style=style)
        output_path = "outputs/TEST_PROPOSAL.docx"
        os.makedirs("outputs", exist_ok=True)

        print("  Generating DOCX document...")
        result_path = generator.generate(state, output_path, "government_canada")

        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✓ DOCX generated successfully")
            print(f"  - Path: {result_path}")
            print(f"  - Size: {file_size:,} bytes")
        else:
            print("✗ DOCX generation failed")

    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Install: pip install python-docx")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_pdf_generator():
    """Test PDF generator."""
    print("\n" + "=" * 60)
    print("TEST 2: PDF Generator")
    print("=" * 60)

    try:
        from rfp.generators.pdf_generator import PDFGenerator

        generator = PDFGenerator()

        print(f"  PDF generation method: {generator.method}")
        print(f"  Available: {generator.is_available()}")

        if generator.is_available():
            # Test with DOCX if it exists
            docx_path = "outputs/TEST_PROPOSAL.docx"
            if os.path.exists(docx_path):
                pdf_path = "outputs/TEST_PROPOSAL.pdf"

                print(f"  Converting DOCX to PDF...")
                result_path = generator.generate_from_docx(docx_path, pdf_path)

                if os.path.exists(result_path):
                    file_size = os.path.getsize(result_path)
                    print(f"✓ PDF generated successfully")
                    print(f"  - Path: {result_path}")
                    print(f"  - Size: {file_size:,} bytes")
                else:
                    print("✗ PDF generation failed")
            else:
                print(f"  ℹ DOCX file not found, skipping conversion test")
                print(f"    Run TEST 1 first to generate DOCX")
        else:
            print("✗ PDF generation not available")
            print("  Install one of:")
            print("    - pip install docx2pdf")
            print("    - brew install libreoffice")
            print("    - pip install pypandoc && brew install pandoc")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_document_styles():
    """Test custom document styling."""
    print("\n" + "=" * 60)
    print("TEST 3: Document Styling")
    print("=" * 60)

    try:
        from rfp.generators.docx_generator import DocumentStyle

        # Test default style
        default_style = DocumentStyle()
        print(f"✓ Default style created")
        print(f"  - Font: {default_style.font_name}")
        print(f"  - Size: {default_style.font_size}pt")
        print(f"  - Company: {default_style.company_name}")

        # Test custom style
        custom_style = DocumentStyle(
            font_name="Calibri",
            font_size=12,
            color_primary=(255, 0, 0),
            company_name="Custom Company Inc."
        )
        print(f"\n✓ Custom style created")
        print(f"  - Font: {custom_style.font_name}")
        print(f"  - Size: {custom_style.font_size}pt")
        print(f"  - Color: RGB{custom_style.color_primary}")
        print(f"  - Company: {custom_style.company_name}")

    except Exception as e:
        print(f"✗ Test failed: {e}")


def test_end_to_end_generation():
    """Test complete end-to-end output generation."""
    print("\n" + "=" * 60)
    print("TEST 4: End-to-End Output Generation")
    print("=" * 60)

    try:
        from rfp.generators.docx_generator import DOCXGenerator
        from rfp.generators.pdf_generator import PDFGenerator

        # Mock minimal state
        state = {
            "project_id": "E2E-TEST-001",
            "status": "valide",
            "rana_score": 90,
            "compliance_score": 95.0,
            "requirements_count": 10,
            "iteration_count": 1,
            "timbo_analysis": "# Test Analysis\nTest content.",
            "zat_blueprint": "# Test Blueprint\nTest content.",
            "mary_deliverable": "# Test Proposal\nTest content.",
            "rana_evaluation": "# Test Evaluation\nScore: 90/100",
            "compliance_matrix": "# Test Matrix",
            "requirements": [],
            "compliance_gaps": []
        }

        os.makedirs("outputs", exist_ok=True)

        # Generate DOCX
        print("  Step 1: Generate DOCX...")
        docx_gen = DOCXGenerator()
        docx_path = "outputs/E2E_TEST.docx"
        docx_gen.generate(state, docx_path, "corporate")
        print(f"  ✓ DOCX created: {docx_path}")

        # Generate PDF
        print("  Step 2: Generate PDF...")
        pdf_gen = PDFGenerator()

        if pdf_gen.is_available():
            pdf_path = "outputs/E2E_TEST.pdf"
            pdf_gen.generate_from_docx(docx_path, pdf_path)
            print(f"  ✓ PDF created: {pdf_path}")
            print(f"\n✓ End-to-end generation successful")
        else:
            print(f"  ⚠ PDF generation not available (skipped)")
            print(f"✓ End-to-end generation successful (DOCX only)")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_integration_with_rfp_workflow():
    """Test integration with RFP orchestrator."""
    print("\n" + "=" * 60)
    print("TEST 5: RFP Workflow Integration")
    print("=" * 60)

    try:
        # Check that agents_rfp has been updated with output generation
        from agents_rfp import RFPOrchestrator

        orchestrator = RFPOrchestrator()

        # Check for _generate_outputs method
        has_method = hasattr(orchestrator, '_generate_outputs')
        print(f"  _generate_outputs method present: {has_method}")

        if has_method:
            print("✓ RFP orchestrator has output generation capability")
        else:
            print("✗ RFP orchestrator missing _generate_outputs method")

    except Exception as e:
        print(f"✗ Test failed: {e}")


def main():
    """Run all Phase 3 tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  KPLW Phase 3 Test Suite".center(58) + "║")
    print("║" + "  DOCX & PDF Output Generation".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    test_docx_generator()
    test_pdf_generator()
    test_document_styles()
    test_end_to_end_generation()
    test_integration_with_rfp_workflow()

    print("\n" + "=" * 60)
    print("Phase 3 Testing Complete")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test full RFP workflow with formats:")
    print("   python main.py --rfp --rfp-files rfp.md --format docx")
    print("2. Test PDF generation:")
    print("   python main.py --rfp --rfp-files rfp.md --format pdf")
    print("3. Test all formats:")
    print("   python main.py --rfp --rfp-files rfp.md --format all")
    print()


if __name__ == "__main__":
    main()
