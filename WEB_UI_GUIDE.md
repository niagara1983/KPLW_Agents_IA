# KPLW RFP Web UI - User Guide

## Overview

The KPLW RFP Web UI provides a beautiful, intuitive interface for generating RFP responses with optional team CV analysis.

## Features

✅ **Drag & Drop File Upload** - Easy RFP document upload
✅ **Team CV Upload** - Optional CV analysis via TESS agent
✅ **Real-time Progress** - Watch the AI agents work in real-time
✅ **Multiple Output Formats** - MD, DOCX, PDF
✅ **Template Selection** - Choose proposal template
✅ **Instant Downloads** - Get your proposal immediately

## Getting Started

### 1. Start the Web Server

```bash
# Option 1: Using the startup script
./start_web_ui.sh

# Option 2: Direct Python
python3 web/server.py
```

The server will start at: **http://localhost:8000**

### 2. Open in Browser

Navigate to `http://localhost:8000` in your web browser.

## Using the Web UI

### Step 1: Upload RFP Documents

1. **Drag & drop** RFP files onto the upload area, OR
2. Click **"Select Files"** to browse

**Supported formats**: PDF, DOCX, MD

**Multiple files**: You can upload multiple RFP documents (main RFP + annexes)

### Step 2: Upload Team CVs (Optional) 🆕

After uploading RFP files, a **second upload section** appears:

- **Green-themed section**: "Upload Team CVs (Optional)"
- Upload resumes of team members who will work on the project
- **TESS agent will analyze** these CVs against RFP requirements
- **Generates tailored profiles** (not full CVs) for the proposal

**Benefits of uploading CVs:**
- ✅ Automatically generates team sections
- ✅ Maps team experience to RFP requirements
- ✅ Identifies qualification gaps early
- ✅ Creates concise, relevant team profiles
- ✅ Improves "Team Qualifications" score (15-30% of RFP evaluation)

**What TESS does:**
```
Your CVs → TESS Analysis → Tailored Team Profiles → Integrated into Proposal
```

### Step 3: Configure Options

**Proposal Template:**
- Government of Canada (default)
- Corporate RFP
- Consulting Services
- International Development
- IT Services

**Output Formats** (select multiple):
- ✅ Markdown (always recommended for review)
- ✅ Word (DOCX) - Client-ready proposal
- ☐ PDF (requires conversion tools)

### Step 4: Generate Proposal

Click **"🚀 Generate RFP Response"**

### Step 5: Watch Real-time Progress

The UI shows live updates as each agent works:

```
[10%] Initializing agents...
[20%] TIMBO analyzing RFP requirements...
[30%] ZAT designing proposal structure...
[40%] TESS analyzing team CVs... (if CVs uploaded)
[50%] MARY generating proposal content...
[75%] RANA validating quality...
[100%] Complete!
```

### Step 6: Download Results

Once complete, you'll see:

**Score Cards:**
- Quality Score (RANA): X/100
- Compliance: X%
- Iterations: X
- Status: VALIDE/ESCALADE

**Download Buttons:**
- 📄 Download Markdown
- 📝 Download DOCX (client-ready proposal)
- ✅ Compliance Matrix
- 📕 Download PDF (if generated)

## Example Workflow

### Without Team CVs:

```
1. Upload: Appel-de-propositions-audit-FCFA.pdf
2. Template: Consulting Services
3. Formats: Markdown + DOCX
4. Click: Generate RFP Response
5. Wait: ~2-3 minutes
6. Download: Proposal ready!
```

### With Team CVs (Recommended):

```
1. Upload RFP: Appel-de-propositions-audit-FCFA.pdf

2. Upload Team CVs:
   - cv_jean_dupont_chef_projet.pdf
   - cv_marie_martin_auditeur.pdf
   - cv_ahmed_kane_analyste.pdf

3. Template: Consulting Services
4. Formats: Markdown + DOCX
5. Click: Generate RFP Response
6. Wait: ~3-4 minutes (extra time for CV analysis)
7. Download: Proposal with tailored team profiles!
```

## CV Upload Best Practices

### Naming CVs

Use clear, descriptive names:
```
✅ cv_jean_dupont_chef_projet.pdf
✅ cv_marie_martin_auditeur_senior.pdf
✅ cv_ahmed_kane_analyste_financier.pdf

❌ resume.pdf
❌ CV 1.pdf
❌ John.docx
```

### CV Format

- **PDF preferred** (best parsing quality)
- DOCX also supported
- Ensure CVs have clear sections:
  - Work Experience
  - Education
  - Certifications
  - Skills

### How Many CVs?

Upload CVs for:
- ✅ Key personnel required by RFP
- ✅ Team members who will actually work on the project
- ✅ People whose experience matches RFP requirements

Typical: 3-6 CVs (Project Manager, Technical Leads, Key Specialists)

## What Gets Generated

### 1. Individual Agent Outputs (in outputs/)

- `{project_id}_1_TIMBO_analyse.md` - RFP analysis
- `{project_id}_2_ZAT_blueprint.md` - Proposal structure
- `{project_id}_2.5_TESS_team_profiles.md` - Tailored team profiles (if CVs uploaded)
- `{project_id}_3_MARY_livrable.md` - Full proposal
- `{project_id}_4_RANA_evaluation.md` - Quality assessment
- `{project_id}_COMPLIANCE_MATRIX.md` - Requirement tracking

### 2. Client-Ready Outputs

- `{project_id}_PROPOSAL.docx` - **Client-ready proposal (MARY only)**
- `{project_id}_PROPOSAL.pdf` - PDF version (if generated)
- `{project_id}_RAPPORT_COMPLET.md` - Full internal report (all agents)

### 3. TESS Team Profiles (if CVs uploaded)

TESS generates:

**Team Summary:**
```markdown
| Name | Role | Exp. | Score |
|------|------|------|-------|
| Jean Dupont | Chef projet | 12 ans | 9/10 |
| Marie Martin | Auditeur | 8 ans | 8/10 |
```

**Requirement Coverage:**
```markdown
✓ R005: "Chef projet 10+ ans" → Jean Dupont
✓ R012: "Certification CPA" → Jean + Marie
⚠ R018: "Expérience audit IT" → Partiellement couvert
```

**Individual Tailored Profiles:**
```markdown
### Jean Dupont, CPA, CIA
**Rôle proposé**: Chef de projet d'audit

**Expérience pertinente**:
- Audit FCFA 5M Ministère Éducation (2022-2023)
  → Adresse requirements R005, R012
  → Score: 9/10

[Only relevant experience included - not full CV!]
```

These profiles are automatically integrated into MARY's proposal.

## Troubleshooting

### Issue: Server won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process if needed
kill -9 <PID>

# Or use different port
uvicorn web.server:app --port 8001
```

### Issue: CV parsing fails

```
⚠ Warning: Could not parse cv_name.pdf
```

**Solutions:**
- Ensure CV is valid PDF/DOCX (not scanned image)
- Try converting to PDF if DOCX fails
- Check file is not password-protected

### Issue: Processing takes too long

**Normal times:**
- Without CVs: 2-3 minutes
- With CVs (3 files): 3-4 minutes
- With iterations: Add 1-2 minutes per iteration

**If stuck:**
- Check browser console for errors
- Check terminal logs for detailed error messages
- Refresh page and try again

### Issue: Download buttons don't work

- Ensure processing completed (status shows "Complete")
- Check `outputs/` directory for generated files
- Refresh page if needed

## Advanced Usage

### Custom Port

```bash
python3 web/server.py --port 8001
```

### Access from Network

```bash
# Start server on all interfaces
python3 web/server.py --host 0.0.0.0

# Access from other devices
http://<your-ip>:8000
```

### Multiple RFPs

You can process multiple RFPs concurrently:
1. Open multiple browser tabs
2. Each tab can upload different RFP
3. Jobs process independently

## API Endpoints

For developers/automation:

**Upload RFP:**
```bash
POST /api/rfp/upload
- Form data: files (RFP docs), cv_files (CVs)
- Query params: template, output_formats
- Returns: job_id
```

**Get Status:**
```bash
GET /api/rfp/status/{job_id}
- Returns: status, progress, result
```

**Download Files:**
```bash
GET /api/rfp/download/{job_id}/{file_type}
- file_type: md, docx, pdf, compliance
- Returns: File download
```

**WebSocket (real-time progress):**
```bash
WS /ws/rfp/{job_id}
- Receives: {progress: X, message: "..."}
```

## Security Notes

⚠️ **This is a local development server**

- Do NOT expose to public internet without authentication
- Files are stored in `uploads/` directory
- Consider adding authentication for production use
- Clean up old uploads periodically

## Tips for Best Results

1. **Upload complete RFP** - Include all documents (main RFP + annexes)
2. **Use team CVs** - Significantly improves proposal quality
3. **Choose right template** - Matches RFP type (government, corporate, etc.)
4. **Review TESS output** - Check team profiles before submission
5. **Iterate if needed** - If score <85, system auto-iterates to improve

## Cost Tracking

To view accumulated costs:

```bash
python3 main.py --cost-report
```

This shows:
- Total cost across all runs (CLI + Web UI)
- Cost per run
- Cost per agent
- Budget status

## Questions?

- **CLI vs Web UI?** Both support team CVs now!
- **Which to use?** Web UI for ease, CLI for automation
- **Can I use both?** Yes! They share the same backend

Enjoy your AI-powered RFP responses! 🚀
