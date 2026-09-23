#!/bin/bash
set -e

echo "=================================================="
echo "  Starting AI Assignment Reviewer (Local Mode)   "
echo "=================================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Check Python venv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r backend/requirements.txt
fi

# Ensure data folders exist
mkdir -p backend/data/uploads backend/data/extracted backend/data/vector_store backend/data/reviews

# Trap SIGINT to kill background jobs cleanly
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "Starting FastAPI Backend on http://127.0.0.1:8000..."
PYTHONPATH=. .venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "Starting React Frontend on http://127.0.0.1:5173..."
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!

echo ""
echo "=================================================="
echo "  AI Assignment Reviewer is now running!         "
echo "  Frontend: http://127.0.0.1:5173                "
echo "  Backend API Docs: http://127.0.0.1:8000/docs   "
echo "  Press Ctrl+C to stop both servers.             "
echo "=================================================="

wait
