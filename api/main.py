"""
KPLW RFP API - Main Application
FastAPI REST API for RFP response generation
"""

import os
import sys
import uuid
import asyncio
from typing import List, Optional
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("[ERROR] FastAPI not installed. Run: pip install fastapi uvicorn python-multipart")
    sys.exit(1)

from agents.rfp_orchestrator import RFPOrchestrator
from rfp.structure import list_templates

# =============================================================================
# Configuration
# =============================================================================

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Job storage (in production, use Redis or database)
jobs = {}

# WebSocket connections for progress updates
ws_connections = {}

# =============================================================================
# Pydantic Models
# =============================================================================

class JobRequest(BaseModel):
    """RFP processing job request."""
    template: str = "government_canada"
    output_formats: List[str] = ["md", "docx"]


class JobStatus(BaseModel):
    """Job status response."""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[dict] = None


class TemplateInfo(BaseModel):
    """Template information."""
    name: str
    display_name: str
    description: str


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="KPLW RFP API",
    description="AI-powered RFP response generation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (web UI)
web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


# =============================================================================
# Helper Functions
# =============================================================================

async def send_progress(job_id: str, progress: int, message: str):
    """Send progress update via WebSocket."""
    if job_id in ws_connections:
        try:
            await ws_connections[job_id].send_json({
                "job_id": job_id,
                "progress": progress,
                "message": message
            })
        except Exception as e:
            print(f"[WS] Error sending progress: {e}")


async def process_rfp_async(
    job_id: str,
    rfp_files: List[Path],
    template: str,
    output_formats: List[str]
):
    """Process RFP in background."""
    try:
        # Update job status
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        await send_progress(job_id, 10, "Starting RFP analysis...")

        # Initialize orchestrator
        orchestrator = RFPOrchestrator()

        # Mock progress updates during processing
        await send_progress(job_id, 20, "Parsing documents...")
        await asyncio.sleep(0.5)

        await send_progress(job_id, 30, "Extracting requirements...")
        await asyncio.sleep(0.5)

        await send_progress(job_id, 40, "TIMBO: Strategic analysis...")
        await asyncio.sleep(0.5)

        # Run RFP workflow (this will take most of the time)
        await send_progress(job_id, 50, "Processing RFP workflow...")

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        state = await loop.run_in_executor(
            None,
            orchestrator.run_rfp,
            [str(f) for f in rfp_files],
            template,
            output_formats
        )

        await send_progress(job_id, 90, "Finalizing outputs...")

        # Update job with results
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        jobs[job_id]["result"] = {
            "project_id": state.get("project_id"),
            "status": state.get("status"),
            "rana_score": state.get("rana_score"),
            "compliance_score": state.get("compliance_score"),
            "iterations": state.get("iteration_count"),
            "generated_files": state.get("generated_files", {}),
        }

        await send_progress(job_id, 100, "RFP processing completed!")

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        await send_progress(job_id, 0, f"Error: {str(e)}")

        import traceback
        traceback.print_exc()


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - serve web UI."""
    web_index = Path(__file__).parent.parent / "web" / "index.html"
    if web_index.exists():
        return FileResponse(str(web_index))
    return {
        "message": "KPLW RFP API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/templates")
async def get_templates():
    """Get available proposal templates."""
    templates = list_templates()

    template_info = {
        "government_canada": {
            "display_name": "Gouvernement du Canada",
            "description": "Modèle pour les appels d'offres du gouvernement canadien (fédéral et provincial)"
        },
        "corporate": {
            "display_name": "RFP Corporatif",
            "description": "Modèle pour les propositions d'entreprises privées"
        },
        "consulting": {
            "display_name": "Services de Conseil",
            "description": "Modèle pour les services de conseil stratégique et consulting"
        },
        "international_development": {
            "display_name": "Développement International",
            "description": "Modèle pour les projets de développement international et coopération"
        },
        "it_services": {
            "display_name": "Services TI",
            "description": "Modèle pour les services informatiques et développement logiciel"
        }
    }

    return {
        "templates": [
            {
                "name": t,
                **template_info.get(t, {"display_name": t, "description": ""})
            }
            for t in templates
        ]
    }


@app.post("/api/rfp/upload")
async def upload_rfp(
    files: List[UploadFile] = File(...),
    template: str = "government_canada",
    output_formats: str = "md,docx"
):
    """
    Upload RFP files and start processing.

    Args:
        files: List of RFP documents (PDF, DOCX, MD)
        template: Proposal template to use
        output_formats: Comma-separated list of output formats

    Returns:
        Job ID for tracking progress
    """
    # Validate files
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "Job created",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "result": None
    }

    # Save uploaded files
    saved_files = []
    for file in files:
        # Create job-specific directory
        job_dir = UPLOAD_DIR / job_id
        job_dir.mkdir(exist_ok=True)

        # Save file
        file_path = job_dir / file.filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        saved_files.append(file_path)

    # Parse output formats
    formats = [f.strip() for f in output_formats.split(",")]

    # Start background processing
    asyncio.create_task(
        process_rfp_async(job_id, saved_files, template, formats)
    )

    return {
        "job_id": job_id,
        "message": "RFP processing started",
        "files_uploaded": len(saved_files)
    }


@app.get("/api/rfp/status/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


@app.get("/api/rfp/result/{job_id}")
async def get_job_result(job_id: str):
    """Get complete job result."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Status: {job['status']}"
        )

    return {
        "job_id": job_id,
        "status": job["status"],
        "result": job["result"],
        "completed_at": job["completed_at"]
    }


@app.get("/api/rfp/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    """
    Download generated file.

    Args:
        job_id: Job ID
        file_type: File type (docx, pdf, md, report)
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    result = job.get("result", {})
    project_id = result.get("project_id")

    if not project_id:
        raise HTTPException(status_code=404, detail="Project ID not found")

    # Map file type to actual file
    file_mapping = {
        "docx": f"{project_id}_PROPOSAL.docx",
        "pdf": f"{project_id}_PROPOSAL.pdf",
        "md": f"{project_id}_RAPPORT_COMPLET.md",
        "report": f"{project_id}_RAPPORT_COMPLET.md",
        "compliance": f"{project_id}_COMPLIANCE_MATRIX.md",
    }

    if file_type not in file_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file_type}")

    file_path = OUTPUT_DIR / file_mapping[file_type]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_type}")

    return FileResponse(
        path=str(file_path),
        filename=file_mapping[file_type],
        media_type="application/octet-stream"
    )


@app.delete("/api/rfp/job/{job_id}")
async def delete_job(job_id: str):
    """Delete job and associated files."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    # Delete uploaded files
    job_dir = UPLOAD_DIR / job_id
    if job_dir.exists():
        import shutil
        shutil.rmtree(job_dir)

    # Remove job from memory
    del jobs[job_id]

    return {"message": "Job deleted successfully"}


@app.websocket("/ws/rfp/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await websocket.accept()
    ws_connections[job_id] = websocket

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()

            # Echo back for heartbeat
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        if job_id in ws_connections:
            del ws_connections[job_id]


# =============================================================================
# Startup/Shutdown Events
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application."""
    print("=" * 60)
    print("  KPLW RFP API Server")
    print("  Version: 1.0.0")
    print("=" * 60)
    print(f"  Upload directory: {UPLOAD_DIR.absolute()}")
    print(f"  Output directory: {OUTPUT_DIR.absolute()}")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("\n[INFO] Shutting down API server...")
    # Close all WebSocket connections
    for ws in ws_connections.values():
        try:
            await ws.close()
        except:
            pass


# =============================================================================
# Run Server (for development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
