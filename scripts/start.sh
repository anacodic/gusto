#!/bin/bash

# Start all services for Gusto

echo "🚀 Starting Gusto services..."

# Start backend
echo "📦 Starting backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and use its Python explicitly
source venv/bin/activate
VENV_PYTHON="./venv/bin/python"

echo "Installing/updating dependencies..."
$VENV_PYTHON -m pip install --upgrade pip --timeout 60 > /dev/null 2>&1
$VENV_PYTHON -m pip install -r requirements.txt --timeout 60 2>&1 | grep -v "already satisfied" || true

echo "Ensuring correct pydantic version..."
$VENV_PYTHON -m pip install 'pydantic>=2.0.0,<2.5.0' --force-reinstall --no-deps > /dev/null 2>&1
$VENV_PYTHON -m pip install 'pydantic-core>=2.14.0,<2.15.0' --force-reinstall > /dev/null 2>&1

echo "Starting backend server..."
# Use venv Python explicitly to avoid system Python issues
$VENV_PYTHON -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Services started!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill \$BACKEND_PID \$FRONTEND_PID; exit" INT TERM
wait
