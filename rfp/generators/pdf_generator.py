"""
PDF Generator for RFP Proposals
Converts DOCX to PDF or generates PDF directly
"""

import os
import subprocess
from typing import Dict, Optional

# Try multiple PDF generation approaches
PDF_METHOD = None

# Method 1: docx2pdf (Windows/Mac with Word installed)
try:
    from docx2pdf import convert as docx2pdf_convert
    PDF_METHOD = "docx2pdf"
except ImportError:
    pass

# Method 2: pypandoc (requires pandoc installation)
if PDF_METHOD is None:
    try:
        import pypandoc
        PDF_METHOD = "pypandoc"
    except ImportError:
        pass

# Method 3: LibreOffice command line (if available)
if PDF_METHOD is None:
    try:
        result = subprocess.run(
            ['which', 'libreoffice'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            PDF_METHOD = "libreoffice"
    except Exception:
        pass

# Method 4: unoconv (if available)
if PDF_METHOD is None:
    try:
        result = subprocess.run(
            ['which', 'unoconv'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            PDF_METHOD = "unoconv"
    except Exception:
        pass


class PDFGenerator:
    """Generate PDF proposals from DOCX or markdown."""

    def __init__(self):
        """Initialize PDF generator."""
        self.method = PDF_METHOD

        if not self.method:
            print("[WARNING] No PDF conversion method available.")
            print("  Install one of:")
            print("  - pip install docx2pdf (requires Microsoft Word)")
            print("  - pip install pypandoc (requires pandoc)")
            print("  - Install LibreOffice: brew install libreoffice")
            print("  - pip install unoconv")

    def is_available(self) -> bool:
        """Check if PDF generation is available."""
        return self.method is not None

    def generate_from_docx(self, docx_path: str, output_path: str) -> str:
        """
        Convert DOCX to PDF.

        Args:
            docx_path: Path to DOCX file
            output_path: Output PDF path

        Returns:
            Path to generated PDF file

        Raises:
            RuntimeError: If PDF generation fails
        """
        if not self.is_available():
            raise RuntimeError("No PDF conversion method available")

        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")

        print(f"  [PDF] Converting using {self.method}...")

        try:
            if self.method == "docx2pdf":
                self._convert_docx2pdf(docx_path, output_path)

            elif self.method == "pypandoc":
                self._convert_pypandoc(docx_path, output_path)

            elif self.method == "libreoffice":
                self._convert_libreoffice(docx_path, output_path)

            elif self.method == "unoconv":
                self._convert_unoconv(docx_path, output_path)

            if os.path.exists(output_path):
                print(f"  [PDF] ✓ Generated: {output_path}")
                return output_path
            else:
                raise RuntimeError("PDF generation failed - file not created")

        except SystemExit as e:
            # docx2pdf sometimes calls sys.exit() on errors
            raise RuntimeError(f"PDF conversion tool exited with error code: {e.code}")

        except Exception as e:
            raise RuntimeError(f"PDF generation failed: {e}")

    def _convert_docx2pdf(self, docx_path: str, output_path: str):
        """Convert using docx2pdf."""
        docx2pdf_convert(docx_path, output_path)

    def _convert_pypandoc(self, docx_path: str, output_path: str):
        """Convert using pypandoc."""
        import pypandoc
        pypandoc.convert_file(
            docx_path,
            'pdf',
            outputfile=output_path,
            extra_args=['--pdf-engine=pdflatex']
        )

    def _convert_libreoffice(self, docx_path: str, output_path: str):
        """Convert using LibreOffice command line."""
        output_dir = os.path.dirname(output_path) or '.'

        # LibreOffice converts in place with specific naming
        result = subprocess.run(
            [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                docx_path
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")

        # LibreOffice creates PDF with same basename
        docx_basename = os.path.splitext(os.path.basename(docx_path))[0]
        generated_pdf = os.path.join(output_dir, f"{docx_basename}.pdf")

        # Rename if needed
        if generated_pdf != output_path and os.path.exists(generated_pdf):
            os.rename(generated_pdf, output_path)

    def _convert_unoconv(self, docx_path: str, output_path: str):
        """Convert using unoconv."""
        result = subprocess.run(
            ['unoconv', '-f', 'pdf', '-o', output_path, docx_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"unoconv conversion failed: {result.stderr}")

    def generate_from_markdown(self, md_path: str, output_path: str) -> str:
        """
        Convert Markdown to PDF.

        Args:
            md_path: Path to markdown file
            output_path: Output PDF path

        Returns:
            Path to generated PDF file

        Raises:
            RuntimeError: If PDF generation fails
        """
        if not self.is_available():
            raise RuntimeError("No PDF conversion method available")

        if not os.path.exists(md_path):
            raise FileNotFoundError(f"Markdown file not found: {md_path}")

        # For markdown, we prefer pypandoc
        if self.method in ["pypandoc", "libreoffice", "unoconv"]:
            try:
                if self.method == "pypandoc":
                    import pypandoc
                    pypandoc.convert_file(
                        md_path,
                        'pdf',
                        outputfile=output_path,
                        extra_args=[
                            '--pdf-engine=pdflatex',
                            '--variable=geometry:margin=1in'
                        ]
                    )
                elif self.method == "libreoffice":
                    self._convert_libreoffice(md_path, output_path)
                elif self.method == "unoconv":
                    self._convert_unoconv(md_path, output_path)

                return output_path

            except Exception as e:
                raise RuntimeError(f"Markdown to PDF conversion failed: {e}")
        else:
            raise RuntimeError(
                "Markdown to PDF requires pypandoc, LibreOffice, or unoconv"
            )


def generate_pdf_from_docx(docx_path: str, output_path: str) -> str:
    """
    Convenience function to convert DOCX to PDF.

    Args:
        docx_path: Path to DOCX file
        output_path: Output PDF path

    Returns:
        Path to generated PDF file
    """
    generator = PDFGenerator()
    return generator.generate_from_docx(docx_path, output_path)


def generate_pdf_from_markdown(md_path: str, output_path: str) -> str:
    """
    Convenience function to convert Markdown to PDF.

    Args:
        md_path: Path to markdown file
        output_path: Output PDF path

    Returns:
        Path to generated PDF file
    """
    generator = PDFGenerator()
    return generator.generate_from_markdown(md_path, output_path)
