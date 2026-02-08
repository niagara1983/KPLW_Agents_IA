#!/bin/bash
# Start KPLW RFP Web UI

echo "🚀 Starting KPLW RFP Web Server..."
echo "="
echo "📍 Web UI will be available at: http://localhost:8000"
echo "="
echo ""

cd "$(dirname "$0")"
python3 web/server.py
