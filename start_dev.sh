#!/bin/bash

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Kill any existing processes on ports 8000 and 8080
echo "Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Wait for ports to be freed
sleep 2

# Start FastAPI backend
echo "Starting FastAPI backend on port 8080..."
cd podcastfy
python -m uvicorn api.fast_app:app --reload --host 0.0.0.0 --port 8080 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..10}; do
    if check_port 8080; then
        echo "Backend started successfully"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "Error: Backend failed to start"
        kill $BACKEND_PID
        exit 1
    fi
    sleep 1
done

# Start frontend server
echo "Starting frontend server on port 8000..."
cd frontend
python server.py &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
for i in {1..10}; do
    if check_port 8000; then
        echo "Frontend started successfully"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "Error: Frontend failed to start"
        kill $BACKEND_PID $FRONTEND_PID
        exit 1
    fi
    sleep 1
done

# Save PIDs to a file for cleanup
echo $BACKEND_PID > ../.dev_pids
echo $FRONTEND_PID >> ../.dev_pids

echo "Development environment started!"
echo "Backend: http://localhost:8080"
echo "Frontend: http://localhost:8000"
echo "Press Ctrl+C to stop all servers"

# Wait for user to press Ctrl+C
trap "kill $(cat ../.dev_pids) 2>/dev/null; rm ../.dev_pids; echo 'Servers stopped'" INT
wait 