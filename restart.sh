#!/bin/bash

# Kill any existing processes on port 3000 and 8000
echo "Stopping any existing servers..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Set environment for backend
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate 3b1b

# Start backend server
echo "Starting Django backend server..."
cd book_summarizer_api
python manage.py runserver 8000 &
BACKEND_PID=$!

# Wait a bit for the backend to start
sleep 3

# Start frontend server
echo "Starting frontend development server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

# Print information and wait
echo "Servers started!"
echo "Backend running on http://localhost:8000 (PID: $BACKEND_PID)"
echo "Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)"
echo "Press Ctrl+C to stop both servers"

# Wait for user to press Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; echo 'Servers stopped!'; exit 0" INT
wait 