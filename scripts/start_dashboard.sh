#!/bin/bash

echo "Starting Biecho "API: http://localhost:5001/api/dashboard"Bot Dashboard..."
echo

echo "Installing Python API dependencies..."
cd "$(dirname "$0")/../api"
pip install -r requirements.txt

echo
echo "Installing React dependencies..."
cd "$(dirname "$0")/../web-dashboard"
npm install

echo
echo "Starting API server in background..."
cd "$(dirname "$0")/../api"
python dashboard_api.py &
API_PID=$!

echo
echo "Starting React development server..."
cd "$(dirname "$0")/../web-dashboard"
sleep 3
npm start &
REACT_PID=$!

echo
echo "Dashboard should be available at:"
echo "Frontend: http://localhost:3001"
echo "API: http://localhost:5001/api/dashboard"
echo
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $API_PID $REACT_PID 2>/dev/null; exit" INT
wait
