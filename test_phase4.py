#!/usr/bin/env python3
"""
Phase 4 Test Script
Test FastAPI endpoints and Web UI functionality
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_fastapi_import():
    """Test FastAPI dependencies are installed."""
    print("\n" + "=" * 60)
    print("TEST 1: FastAPI Dependencies")
    print("=" * 60)

    try:
        import fastapi
        import uvicorn
        from fastapi import File, UploadFile
        import websockets

        print(f"✓ FastAPI installed: v{fastapi.__version__}")
        print(f"✓ Uvicorn installed: v{uvicorn.__version__}")
        print(f"✓ WebSockets installed")
        print(f"✓ File upload support available")

    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Install: pip install fastapi uvicorn[standard] python-multipart websockets")
        return False

    return True


def test_api_structure():
    """Test API module structure."""
    print("\n" + "=" * 60)
    print("TEST 2: API Module Structure")
    print("=" * 60)

    try:
        from api import main as api_main

        print("✓ API module imported")

        # Check for FastAPI app
        if hasattr(api_main, 'app'):
            print("✓ FastAPI app instance found")

            # Check routes
            routes = [route.path for route in api_main.app.routes]
            expected_routes = [
                "/",
                "/health",
                "/api/templates",
                "/api/rfp/upload",
                "/api/rfp/status/{job_id}",
                "/api/rfp/result/{job_id}",
                "/api/rfp/download/{job_id}/{file_type}",
            ]

            found_routes = []
            for expected in expected_routes:
                # Simple path matching (not exact due to route parameters)
                base_path = expected.split('{')[0].rstrip('/')
                if any(base_path in route for route in routes):
                    found_routes.append(expected)

            print(f"✓ Found {len(found_routes)}/{len(expected_routes)} expected routes")
            for route in found_routes:
                print(f"  - {route}")

        else:
            print("✗ FastAPI app not found")
            return False

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_web_ui_files():
    """Test Web UI files exist."""
    print("\n" + "=" * 60)
    print("TEST 3: Web UI Files")
    print("=" * 60)

    web_dir = Path("web")
    index_file = web_dir / "index.html"

    if not web_dir.exists():
        print(f"✗ Web directory not found: {web_dir}")
        return False

    print(f"✓ Web directory exists: {web_dir}")

    if not index_file.exists():
        print(f"✗ Index file not found: {index_file}")
        return False

    print(f"✓ Index file exists: {index_file}")

    # Check file size
    file_size = index_file.stat().st_size
    print(f"✓ Index file size: {file_size:,} bytes")

    # Check for key HTML elements
    content = index_file.read_text()
    required_elements = [
        "KPLW RFP Generator",
        "upload-section",
        "progress-section",
        "results-section",
        "WebSocket",
        "fetch('/api/"
    ]

    for element in required_elements:
        if element in content:
            print(f"✓ Found: {element}")
        else:
            print(f"✗ Missing: {element}")

    return True


def test_docker_files():
    """Test Docker configuration files."""
    print("\n" + "=" * 60)
    print("TEST 4: Docker Configuration")
    print("=" * 60)

    dockerfile = Path("Dockerfile")
    docker_compose = Path("docker-compose.yml")
    dockerignore = Path(".dockerignore")

    files_ok = True

    if dockerfile.exists():
        print(f"✓ Dockerfile exists ({dockerfile.stat().st_size} bytes)")

        content = dockerfile.read_text()
        if "FROM python:" in content:
            print("  ✓ Base image specified")
        if "uvicorn" in content:
            print("  ✓ Uvicorn command found")
        if "EXPOSE 8000" in content:
            print("  ✓ Port 8000 exposed")
    else:
        print("✗ Dockerfile not found")
        files_ok = False

    if docker_compose.exists():
        print(f"✓ docker-compose.yml exists ({docker_compose.stat().st_size} bytes)")

        content = docker_compose.read_text()
        if "api:" in content:
            print("  ✓ API service defined")
        if "8000:8000" in content:
            print("  ✓ Port mapping configured")
        if "ANTHROPIC_API_KEY" in content:
            print("  ✓ Environment variables configured")
    else:
        print("✗ docker-compose.yml not found")
        files_ok = False

    if dockerignore.exists():
        print(f"✓ .dockerignore exists ({dockerignore.stat().st_size} bytes)")
    else:
        print("✗ .dockerignore not found")
        files_ok = False

    return files_ok


def test_api_server_startup():
    """Test API server can start (dry run)."""
    print("\n" + "=" * 60)
    print("TEST 5: API Server Startup (Dry Run)")
    print("=" * 60)

    try:
        from api.main import app

        print("✓ FastAPI app loaded successfully")

        # Get app metadata
        print(f"  - Title: {app.title}")
        print(f"  - Version: {app.version}")
        print(f"  - Description: {app.description}")

        # Count routes
        routes = [route for route in app.routes]
        print(f"  - Routes: {len(routes)} endpoints")

        # Check middleware
        middleware_count = len(app.user_middleware)
        print(f"  - Middleware: {middleware_count} configured")

        print("\n✓ API server configuration valid")
        print("  To start server: uvicorn api.main:app --reload")
        print("  Or with Docker: docker-compose up")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_integration():
    """Test integration between components."""
    print("\n" + "=" * 60)
    print("TEST 6: Component Integration")
    print("=" * 60)

    try:
        # Check API can import RFP orchestrator
        from api.main import RFPOrchestrator

        print("✓ API can import RFPOrchestrator")

        # Check API can access templates
        from api.main import list_templates

        templates = list_templates()
        print(f"✓ API can access {len(templates)} templates")

        # Check paths
        from api.main import UPLOAD_DIR, OUTPUT_DIR

        print(f"✓ Upload directory configured: {UPLOAD_DIR}")
        print(f"✓ Output directory configured: {OUTPUT_DIR}")

        # Check directories exist
        UPLOAD_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)

        print("✓ Directories created successfully")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Run all Phase 4 tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  KPLW Phase 4 Test Suite".center(58) + "║")
    print("║" + "  Web UI & REST API".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    results.append(("FastAPI Dependencies", test_fastapi_import()))
    results.append(("API Module Structure", test_api_structure()))
    results.append(("Web UI Files", test_web_ui_files()))
    results.append(("Docker Configuration", test_docker_files()))
    results.append(("API Server Startup", test_api_server_startup()))
    results.append(("Component Integration", test_integration()))

    print("\n" + "=" * 60)
    print("Phase 4 Testing Complete")
    print("=" * 60)

    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nResults: {passed}/{total} tests passed")

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")

    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("\n1. Install dependencies:")
    print("   pip install fastapi uvicorn[standard] python-multipart websockets")
    print("\n2. Start the API server:")
    print("   python api/main.py")
    print("   Or: uvicorn api.main:app --reload --port 8000")
    print("\n3. Open web UI:")
    print("   http://localhost:8000")
    print("\n4. View API docs:")
    print("   http://localhost:8000/docs")
    print("\n5. Deploy with Docker:")
    print("   docker-compose up --build")
    print()


if __name__ == "__main__":
    main()
