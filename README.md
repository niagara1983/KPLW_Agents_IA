# KPLW RFP Response Generator

AI-powered RFP response generation system using multi-agent architecture.

**Version:** 2.0.0
**Status:** Production Ready ✅

---

## Overview

KPLW is a sophisticated multi-agent AI system for generating professional RFP (Request for Proposal) responses. It uses four specialized agents working in concert:

- **TIMBO**: Strategic RFP Analysis
- **ZAT**: Proposal Structure Design
- **MARY**: Content Generation
- **RANA**: Quality & Compliance Validation

## Features

✅ **Multi-provider LLM support** (Anthropic, OpenAI, Azure, Ollama)
✅ **Vision-capable document parsing** (PDF, DOCX, MD)
✅ **Automated compliance matrix generation**
✅ **Multi-format output** (Markdown, DOCX, PDF)
✅ **8-stage RFP pipeline** with iterative refinement
✅ **Web UI + REST API** for easy access
✅ **Docker deployment** ready
✅ **Cost tracking** and budget enforcement

---

## Quick Start

### Prerequisites

```bash
# Python 3.11+
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create `.env` file:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
OPENAI_API_KEY=sk-...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=https://...

# Budget limit (USD)
BUDGET_LIMIT_USD=100.0

# Vision parsing
VISION_ENABLED=true
```

---

## Usage

### Option 1: Web UI (Recommended)

**Start the server:**

```bash
# Development mode (with auto-reload)
python3 api/main.py

# Or production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Access the UI:**

Open browser to: **http://localhost:8000**

**Features:**
- Drag-and-drop file upload
- Template selection
- Real-time progress tracking
- Download generated proposals (DOCX/PDF)
- WebSocket live updates

---

### Option 2: Command Line Interface

**Process an RFP:**

```bash
python3 main.py --rfp \
  --rfp-files path/to/rfp.pdf \
  --template government_canada \
  --format md,docx,pdf
```

**Arguments:**

- `--rfp` - Enable RFP mode (required)
- `--rfp-files` - RFP document paths (PDF, DOCX, MD)
- `--template` - Proposal template (see Templates below)
- `--format` - Output formats: `md`, `docx`, `pdf`, or `all`
- `--output` - Output directory (default: `outputs/`)

**Example:**

```bash
python3 main.py --rfp \
  --rfp-files rfp_main.pdf rfp_annex.docx \
  --template government_canada \
  --format all
```

---

## Templates

Five professional proposal templates available:

| Template | Description | Best For |
|----------|-------------|----------|
| `government_canada` | Federal government RFP format | Canadian government bids |
| `corporate` | Business-focused proposal | Private sector RFPs |
| `consulting` | Professional services | Consulting engagements |
| `international_development` | Development projects | NGO/multilateral RFPs |
| `it_services` | Technology solutions | IT/software RFPs |

---

## API Endpoints

### REST API

**Base URL:** `http://localhost:8000`

#### Upload RFP
```http
POST /api/rfp/upload
Content-Type: multipart/form-data

files: [file1.pdf, file2.docx]
template: government_canada
output_formats: md,docx
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "message": "RFP processing started",
  "files_uploaded": 2
}
```

#### Check Status
```http
GET /api/rfp/status/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 65,
  "message": "MARY: Generating proposal content..."
}
```

#### Download Results
```http
GET /api/rfp/download/{job_id}/docx
GET /api/rfp/download/{job_id}/pdf
GET /api/rfp/download/{job_id}/report
```

#### WebSocket (Real-time Updates)
```javascript
ws://localhost:8000/ws/rfp/{job_id}
```

### API Documentation

Interactive docs: **http://localhost:8000/docs**

---

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t kplw-rfp .

# Run container
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your-key \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  kplw-rfp
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services:**
- API server on port 8000
- Automatic restart
- Volume persistence

---

## Architecture

### 8-Stage RFP Pipeline

```
┌─────────────────────────────────────────────────────┐
│  STAGE 1: Document Parsing                         │
│  • PDF/DOCX/MD extraction                          │
│  • Vision-based table/image processing             │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 2: Requirement Extraction                   │
│  • LLM-powered requirement identification          │
│  • Mandatory vs. optional classification           │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 3: TIMBO - Strategic Analysis               │
│  • RFP analysis & opportunity assessment           │
│  • Win themes & risk identification                │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 4: ZAT - Proposal Structure                 │
│  • Template-based structure design                 │
│  • Requirement mapping to sections                 │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 5: MARY ↔ RANA Loop (max 3 iterations)     │
│  • MARY: Content generation                        │
│  • RANA: Quality validation (10 dimensions)        │
│  • Iterative refinement until score ≥ 85/100      │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 6: Compliance Matrix                        │
│  • Requirement-to-section mapping                  │
│  • Gap analysis & compliance scoring               │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 7: Final RANA Validation                    │
│  • Complete proposal evaluation                    │
│  • 10-dimension quality assessment                 │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 8: Output Generation                        │
│  • DOCX with professional formatting               │
│  • PDF conversion (multiple methods)               │
│  • Markdown report                                 │
└─────────────────────────────────────────────────────┘
```

### Agent Architecture

```
agents/
├── base.py                 # LLMClient, BaseAgent, ProjectState
├── timbo.py               # Strategic analysis agent
├── zat.py                 # Structure design agent
├── mary.py                # Content generation agent
├── rana.py                # Quality validation agent
└── rfp_orchestrator.py    # Main workflow coordinator
```

---

## Output Files

For each RFP processed, the system generates:

| File | Description |
|------|-------------|
| `{project_id}_PROPOSAL.docx` | Professional DOCX proposal |
| `{project_id}_PROPOSAL.pdf` | PDF version (if requested) |
| `{project_id}_COMPLIANCE_MATRIX.md` | Requirement compliance matrix |
| `{project_id}_RAPPORT_COMPLET.md` | Complete workflow report |
| `{project_id}_1_TIMBO_analyse.md` | TIMBO analysis output |
| `{project_id}_2_ZAT_blueprint.md` | ZAT structure blueprint |
| `{project_id}_3_MARY_livrable.md` | MARY content output |
| `{project_id}_4_RANA_evaluation.md` | RANA evaluation report |

---

## Configuration

### Model Selection

Configure models per agent/task in `.env`:

```bash
# Strategic analysis (Opus for best quality)
TIMBO_ANALYSIS_MODEL=claude-opus-4-5-20251101

# Content generation (Sonnet for balance)
MARY_CONTENT_MODEL=claude-sonnet-4-5-20250929

# Fast tasks (Haiku for efficiency)
RANA_EVALUATION_MODEL=claude-haiku-4-5-20251001
```

### Quality Settings

```bash
# Minimum acceptable score (0-100)
QUALITY_THRESHOLD=85

# Maximum refinement iterations
MAX_ITERATIONS=3

# Temperature for creativity
TEMPERATURE=0.7
```

---

## Testing

### Run Test Suite

```bash
# Phase 2 tests (RFP core functionality)
python3 test_phase2.py
```

**Tests:**
- ✅ Compliance extractor
- ✅ Compliance matrix generation
- ✅ Proposal structure templates
- ✅ RFP prompts loading
- ✅ RFP orchestrator initialization

---

## Troubleshooting

### PDF Generation Not Working

Install system dependencies:

```bash
# macOS
brew install libreoffice pandoc

# Ubuntu/Debian
apt-get install libreoffice pandoc

# Or Python package
pip install docx2pdf
```

### Vision Parsing Issues

Check dependencies:

```bash
pip install PyMuPDF pillow
```

Disable vision if needed:
```bash
VISION_ENABLED=false
```

### Anthropic API Errors

If you see `socket_options` error:
- This is a known compatibility issue
- System will gracefully fallback to simulation mode
- Or use Ollama for local inference

---

## Development

### Project Structure

```
KPLW_Agents_IA/
├── agents/                # Multi-agent system
│   ├── base.py           # Base classes
│   ├── timbo.py          # TIMBO agent
│   ├── zat.py            # ZAT agent
│   ├── mary.py           # MARY agent
│   ├── rana.py           # RANA agent
│   └── rfp_orchestrator.py
├── llm/                  # LLM abstraction
│   ├── providers.py      # Multi-provider support
│   └── router.py         # Model routing & cost tracking
├── document/             # Document parsing
│   └── parser.py         # PDF/DOCX/MD parser
├── rfp/                  # RFP-specific logic
│   ├── compliance.py     # Compliance matrix
│   ├── structure.py      # Proposal templates
│   └── generators/       # Output generation
│       ├── docx_generator.py
│       └── pdf_generator.py
├── api/                  # FastAPI backend
│   └── main.py
├── web/                  # Web UI
│   └── index.html
├── prompts_rfp.py        # RFP-specific prompts
├── config.py             # Configuration
└── main.py               # CLI entry point
```

### Adding New Templates

1. Edit `rfp/structure.py`
2. Add new `ProposalStructure` to `PROPOSAL_TEMPLATES`
3. Define sections with order, page limits, requirements

### Extending Agents

Each agent has specialized methods:

```python
from agents import TIMBOAgent, LLMClient

llm = LLMClient()
timbo = TIMBOAgent(llm)

# Use specialized methods
analysis = timbo.analyze_rfp(rfp_text)
go_no_go = timbo.assess_go_no_go(rfp_text)
themes = timbo.extract_win_themes(analysis)
```

---

## Cost Management

Track API costs in real-time:

```python
from agents.rfp_orchestrator import RFPOrchestrator

orchestrator = RFPOrchestrator()
state = orchestrator.run_rfp(rfp_files=["rfp.pdf"])

# View costs
cost = state["cost_summary"]
print(f"Total: ${cost['total_cost']:.2f}")
print(f"Calls: {cost['num_calls']}")
```

Set budget limits:
```bash
BUDGET_LIMIT_USD=50.0  # Stops processing if exceeded
```

---

## License

Proprietary - KPLW Strategic Innovations Inc.

---

## Support

For issues or questions:
- Check documentation in `docs/` folder
- Review `AGENT_RESTRUCTURING.md` for architecture details
- Contact: support@kplw.com

---

**Status:** Production Ready ✅
**Last Updated:** February 7, 2026
**Version:** 2.0.0
