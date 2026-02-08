"""
KPLW RFP Web Server
FastAPI backend for web UI
"""

import os
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import shutil

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rfp_orchestrator import RFPOrchestrator
from rfp.structure import get_all_templates

# Initialize FastAPI
app = FastAPI(title="KPLW RFP Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="web"), name="static")

# Storage for active jobs
jobs = {}
websocket_connections = {}

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


class JobManager:
    """Manages RFP processing jobs."""

    def __init__(self):
        self.jobs = {}

    def create_job(self, rfp_files: List[str], cv_files: List[str], template: str, formats: List[str]) -> str:
        """Create a new job."""
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            'id': job_id,
            'status': 'pending',
            'progress': 0,
            'message': 'Initializing...',
            'rfp_files': rfp_files,
            'cv_files': cv_files,
            'template': template,
            'formats': formats,
            'result': None,
            'error': None,
            'created_at': datetime.now().isoformat()
        }
        return job_id

    def get_job(self, job_id: str):
        """Get job by ID."""
        return self.jobs.get(job_id)

    def update_job(self, job_id: str, **kwargs):
        """Update job fields."""
        if job_id in self.jobs:
            self.jobs[job_id].update(kwargs)

    async def send_progress(self, job_id: str, progress: int, message: str):
        """Send progress update via WebSocket."""
        self.update_job(job_id, progress=progress, message=message)

        if job_id in websocket_connections:
            try:
                await websocket_connections[job_id].send_json({
                    'progress': progress,
                    'message': message
                })
            except:
                pass


job_manager = JobManager()


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse("web/index.html")


@app.get("/api/templates")
async def get_templates():
    """Get available proposal templates."""
    templates = get_all_templates()
    return {
        "templates": [
            {
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description
            }
            for t in templates
        ]
    }


@app.post("/api/rfp/upload")
async def upload_rfp(
    files: List[UploadFile] = File(...),
    cv_files: Optional[List[UploadFile]] = File(None),
    template: str = Query("government_canada"),
    output_formats: str = Query("md,docx")
):
    """
    Upload RFP files and optionally CV files.

    Args:
        files: RFP document files
        cv_files: Optional team member CV files
        template: Proposal template name
        output_formats: Comma-separated output formats
    """
    try:
        # Create job ID
        job_id = str(uuid.uuid4())
        job_dir = UPLOAD_DIR / job_id
        job_dir.mkdir(exist_ok=True)

        # Save RFP files
        rfp_file_paths = []
        for file in files:
            file_path = job_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            rfp_file_paths.append(str(file_path))

        # Save CV files if provided
        cv_file_paths = []
        if cv_files:
            for file in cv_files:
                file_path = job_dir / f"cv_{file.filename}"
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                cv_file_paths.append(str(file_path))

        # Parse output formats
        formats = [f.strip() for f in output_formats.split(',')]

        # Create job
        job_manager.create_job(
            rfp_files=rfp_file_paths,
            cv_files=cv_file_paths,
            template=template,
            formats=formats
        )

        # Start processing in background
        asyncio.create_task(process_rfp_job(job_id))

        return JSONResponse({
            "job_id": job_id,
            "message": "Processing started",
            "cv_count": len(cv_file_paths) if cv_file_paths else 0
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_rfp_job(job_id: str):
    """Process RFP job in background."""
    try:
        job = job_manager.get_job(job_id)

        # Update progress
        await job_manager.send_progress(job_id, 10, "Initializing agents...")

        # Create orchestrator
        orchestrator = RFPOrchestrator()

        await job_manager.send_progress(job_id, 20, "Running TIMBO analysis...")

        # Run RFP workflow
        cv_files = job['cv_files'] if job['cv_files'] else None

        result = orchestrator.run_rfp(
            rfp_files=job['rfp_files'],
            template_name=job['template'],
            output_formats=job['formats'],
            team_cvs=cv_files  # Pass CV files to orchestrator
        )

        await job_manager.send_progress(job_id, 100, "Complete!")

        # Update job with result
        job_manager.update_job(
            job_id,
            status='completed',
            result={
                'rana_score': result.get('rana_score', 0),
                'compliance_score': result.get('compliance_score', 0),
                'iterations': result.get('iteration_count', 0),
                'status': result.get('status', 'unknown'),
                'project_id': result.get('project_id'),
                'generated_files': result.get('generated_files', {})
            }
        )

    except Exception as e:
        job_manager.update_job(
            job_id,
            status='failed',
            error=str(e)
        )
        await job_manager.send_progress(job_id, 0, f"Error: {str(e)}")


@app.get("/api/rfp/status/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@app.websocket("/ws/rfp/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await websocket.accept()
    websocket_connections[job_id] = websocket

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == 'ping':
                await websocket.send_text('pong')
    except WebSocketDisconnect:
        if job_id in websocket_connections:
            del websocket_connections[job_id]


@app.get("/api/rfp/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    """Download generated files."""
    job = job_manager.get_job(job_id)
    if not job or job['status'] != 'completed':
        raise HTTPException(status_code=404, detail="Job not found or not completed")

    project_id = job['result']['project_id']
    output_dir = Path("outputs")

    # Determine file path based on type
    if file_type == "md":
        file_path = output_dir / f"{project_id}_RAPPORT_COMPLET.md"
        media_type = "text/markdown"
    elif file_type == "docx":
        file_path = output_dir / f"{project_id}_PROPOSAL.docx"
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif file_type == "pdf":
        file_path = output_dir / f"{project_id}_PROPOSAL.pdf"
        media_type = "application/pdf"
    elif file_type == "compliance":
        file_path = output_dir / f"{project_id}_COMPLIANCE_MATRIX.md"
        media_type = "text/markdown"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=file_path.name
    )


if __name__ == "__main__":
    print("🚀 Starting KPLW RFP Web Server...")
    print("📍 Open http://localhost:8000 in your browser")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
