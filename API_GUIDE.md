# KPLW RFP API Guide
## REST API & Web UI Documentation

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file with your API keys:

```bash
# LLM Provider
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # Optional

# Configuration
DEFAULT_PROVIDER=anthropic
VISION_ENABLED=true
BUDGET_LIMIT_USD=100.0
```

### 3. Start the Server

```bash
# Option 1: Direct Python
python api/main.py

# Option 2: Uvicorn (recommended for development)
uvicorn api.main:app --reload --port 8000

# Option 3: Docker
docker-compose up --build
```

### 4. Access the Application

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📡 API Endpoints

### Health & Info

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-07T19:00:00.000000",
  "version": "1.0.0"
}
```

#### `GET /api/templates`
Get available proposal templates.

**Response:**
```json
{
  "templates": [
    {
      "name": "government_canada",
      "display_name": "Government of Canada",
      "description": "Federal government RFP format with compliance matrix"
    },
    ...
  ]
}
```

### RFP Processing

#### `POST /api/rfp/upload`
Upload RFP documents and start processing.

**Parameters:**
- `files` (form-data): List of files to upload (PDF, DOCX, MD)
- `template` (query): Template name (default: government_canada)
- `output_formats` (query): Comma-separated formats (default: md,docx)

**Request:**
```bash
curl -X POST http://localhost:8000/api/rfp/upload \
  -F "files=@rfp.pdf" \
  -F "files=@technical_annex.docx" \
  "?template=consulting&output_formats=md,docx,pdf"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "RFP processing started",
  "files_uploaded": 2
}
```

#### `GET /api/rfp/status/{job_id}`
Get job processing status.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "message": "MARY: Generating proposal content...",
  "started_at": "2026-02-07T19:00:00.000000",
  "completed_at": null
}
```

**Status Values:**
- `pending`: Job created, not started
- `processing`: Currently processing
- `completed`: Successfully completed
- `failed`: Processing failed

#### `GET /api/rfp/result/{job_id}`
Get complete job result (only when completed).

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "project_id": "RFP-20260207-190000",
    "status": "valide",
    "rana_score": 85,
    "compliance_score": 92.5,
    "iterations": 2,
    "generated_files": {
      "docx": "outputs/RFP-20260207-190000_PROPOSAL.docx",
      "pdf": "outputs/RFP-20260207-190000_PROPOSAL.pdf"
    }
  },
  "completed_at": "2026-02-07T19:05:00.000000"
}
```

#### `GET /api/rfp/download/{job_id}/{file_type}`
Download generated files.

**File Types:**
- `docx`: Word document proposal
- `pdf`: PDF proposal (if generated)
- `md` or `report`: Complete markdown report
- `compliance`: Compliance matrix

**Example:**
```bash
curl -O http://localhost:8000/api/rfp/download/{job_id}/docx
```

#### `DELETE /api/rfp/job/{job_id}`
Delete job and associated files.

**Response:**
```json
{
  "message": "Job deleted successfully"
}
```

### WebSocket

#### `WS /ws/rfp/{job_id}`
Real-time progress updates via WebSocket.

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/rfp/{job_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}%`);
  console.log(`Message: ${data.message}`);
};

// Keep alive
setInterval(() => ws.send('ping'), 30000);
```

**Messages Received:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 50,
  "message": "Processing RFP workflow..."
}
```

---

## 🌐 Web UI Usage

### 1. Upload RFP Files

- Drag and drop files onto the upload area
- Or click "Select Files" to browse
- Supported formats: PDF, DOCX, MD
- Multiple files can be uploaded

### 2. Configure Processing

- **Template**: Select proposal template
  - Government of Canada
  - Corporate RFP
  - Consulting Services
  - International Development
  - IT Services

- **Output Formats**: Select desired formats
  - ✓ Markdown (reports and analysis)
  - ✓ DOCX (professional proposals)
  - ✓ PDF (requires conversion tools)

### 3. Process RFP

Click "🚀 Generate RFP Response"

**Processing Stages:**
1. Document Parsing (10%)
2. Requirement Extraction (20-30%)
3. TIMBO Strategic Analysis (40%)
4. ZAT Structure Design (50%)
5. MARY Content Generation (60-70%)
6. Compliance Mapping (80%)
7. RANA Validation (90%)
8. Output Generation (100%)

### 4. View Results

Upon completion:
- **Quality Score**: RANA quality rating (0-100)
- **Compliance**: Requirement coverage percentage
- **Iterations**: Number of refinement cycles
- **Status**: Final validation status

### 5. Download Files

Click download buttons for:
- 📄 Markdown Report
- 📝 DOCX Proposal
- 📕 PDF Proposal (if available)
- ✅ Compliance Matrix

---

## 🐳 Docker Deployment

### Development

```bash
# Build and start
docker-compose up --build

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Production

```bash
# Build production image
docker build -t kplw-rfp:latest .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key \
  -e BUDGET_LIMIT_USD=100 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  --name kplw-rfp-api \
  kplw-rfp:latest

# Check health
curl http://localhost:8000/health
```

### Docker Compose Configuration

The `docker-compose.yml` includes:
- **API Service**: Main application
- **Ollama** (optional): Local LLM models
- **Redis** (optional): Job queue and caching
- **PostgreSQL** (optional): Persistent storage

Uncomment services as needed in `docker-compose.yml`.

---

## 🔧 Configuration

### Environment Variables

```bash
# === LLM Providers ===
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://...
DEFAULT_PROVIDER=anthropic

# === Features ===
VISION_ENABLED=true              # Enable vision models
SIMULATION_MODE=false            # Use mock responses

# === Budget ===
BUDGET_LIMIT_USD=100.0           # Cost limit
COST_TRACKING_ENABLED=true

# === Quality ===
QUALITY_THRESHOLD=80             # RANA threshold
MAX_ITERATIONS=3                 # Max refinement loops

# === Model Routing ===
TIMBO_ANALYSIS_MODEL=claude-opus-4-5-20251101
ZAT_STRUCTURE_MODEL=claude-sonnet-4-5-20250929
MARY_CONTENT_MODEL=claude-sonnet-4-5-20250929
RANA_VALIDATION_MODEL=claude-sonnet-4-5-20250929

# === Server ===
LOG_LEVEL=INFO
```

### Model Selection

Configure per-agent models in `.env`:

```bash
# High-quality strategic analysis
TIMBO_ANALYSIS_MODEL=claude-opus-4-5-20251101

# Balanced structure design
ZAT_STRUCTURE_MODEL=claude-sonnet-4-5-20250929

# Cost-effective content generation
MARY_CONTENT_MODEL=claude-sonnet-4-5-20250929

# Fast quality validation
RANA_VALIDATION_MODEL=claude-haiku-4-5-20251001
```

---

## 📊 Monitoring

### Logs

```bash
# Docker logs
docker-compose logs -f api

# Application logs
tail -f logs/api.log
```

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/templates | jq
```

### Metrics

Job status provides:
- Processing time
- Quality scores
- Compliance percentage
- API costs (if enabled)

---

## 🔒 Security

### Best Practices

1. **API Keys**: Use environment variables, never commit `.env`
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Add rate limiting middleware for production
4. **Authentication**: Implement auth for production deployments
5. **File Validation**: API validates file types and sizes
6. **Sandboxing**: Files stored in isolated directories

### Production Recommendations

```python
# In api/main.py for production:

# Restrict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/rfp/upload")
@limiter.limit("5/minute")
async def upload_rfp(...):
    ...
```

---

## 🧪 Testing

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/health

# Get templates
curl http://localhost:8000/api/templates

# Upload RFP (with test file)
curl -X POST http://localhost:8000/api/rfp/upload \
  -F "files=@test_rfp.pdf" \
  "?template=corporate&output_formats=md,docx"

# Get status (replace JOB_ID)
curl http://localhost:8000/api/rfp/status/{JOB_ID}

# Download result
curl -O http://localhost:8000/api/rfp/download/{JOB_ID}/docx
```

### Automated Testing

```bash
# Run Phase 4 tests
python test_phase4.py

# Test with pytest (if configured)
pytest tests/test_api.py -v
```

---

## 🐛 Troubleshooting

### API Won't Start

```bash
# Check port availability
lsof -i :8000

# Check dependencies
pip list | grep fastapi

# Check environment
python -c "import api.main; print('OK')"
```

### WebSocket Connection Fails

- Check CORS settings
- Verify WebSocket protocol (ws:// or wss://)
- Check firewall/proxy settings

### File Upload Fails

- Check file size limits
- Verify file format (PDF, DOCX, MD)
- Check upload directory permissions

### Processing Stalls

- Check API key validity
- Verify budget limits not exceeded
- Check logs for errors
- Monitor system resources

---

## 📈 Performance

### Optimization Tips

1. **Use Haiku for Fast Tasks**: Configure RANA with Haiku model
2. **Enable Caching**: Use Redis for repeated requests
3. **Batch Processing**: Process multiple RFPs in parallel
4. **Resource Limits**: Set appropriate Docker memory limits

### Expected Performance

- **Small RFP** (1 doc, <50 pages): 2-5 minutes
- **Medium RFP** (2-3 docs, 50-100 pages): 5-10 minutes
- **Large RFP** (5+ docs, 100+ pages): 10-30 minutes

*Times depend on model selection and API response times*

---

## 🆘 Support

For issues and questions:
- Check logs: `docker-compose logs -f api`
- Review documentation: `/docs` endpoint
- Test health: `curl http://localhost:8000/health`
- Verify environment: `.env` configuration

---

**KPLW RFP API v1.0.0** | Multi-Agent AI System
