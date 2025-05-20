#!/bin/bash

echo "==================================================="
echo "   SupplyLine MRO Suite - Development Environment"
echo "==================================================="
echo

echo "Starting development servers..."
echo

# Store the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js v14+ and try again."
    exit 1
fi

# Create database directory if it doesn't exist
if [ ! -d "$PROJECT_ROOT/database" ]; then
    echo "Creating database directory..."
    mkdir -p "$PROJECT_ROOT/database"
fi

# Create flask_session directory if it doesn't exist
if [ ! -d "$PROJECT_ROOT/flask_session" ]; then
    echo "Creating flask_session directory..."
    mkdir -p "$PROJECT_ROOT/flask_session"
fi

# Start backend server in a new terminal
echo "Starting backend server..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_ROOT/backend' && echo 'Activating virtual environment if it exists...' && if [ -f venv/bin/activate ]; then source venv/bin/activate; else echo 'No virtual environment found, continuing without it...'; fi && echo 'Installing backend dependencies...' && pip install -r requirements.txt && echo 'Starting Flask server...' && python run.py\""
else
    # Linux
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$PROJECT_ROOT/backend' && echo 'Activating virtual environment if it exists...' && if [ -f venv/bin/activate ]; then source venv/bin/activate; else echo 'No virtual environment found, continuing without it...'; fi && echo 'Installing backend dependencies...' && pip install -r requirements.txt && echo 'Starting Flask server...' && python run.py; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$PROJECT_ROOT/backend' && echo 'Activating virtual environment if it exists...' && if [ -f venv/bin/activate ]; then source venv/bin/activate; else echo 'No virtual environment found, continuing without it...'; fi && echo 'Installing backend dependencies...' && pip install -r requirements.txt && echo 'Starting Flask server...' && python run.py; exec bash"
    else
        echo "Could not find a suitable terminal emulator. Please start the backend server manually."
        echo "cd '$PROJECT_ROOT/backend' && python run.py"
    fi
fi

# Start frontend server in a new terminal
echo "Starting frontend server..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_ROOT/frontend' && echo 'Installing frontend dependencies...' && npm install && echo 'Starting Vite development server...' && npm run dev\""
else
    # Linux
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$PROJECT_ROOT/frontend' && echo 'Installing frontend dependencies...' && npm install && echo 'Starting Vite development server...' && npm run dev; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$PROJECT_ROOT/frontend' && echo 'Installing frontend dependencies...' && npm install && echo 'Starting Vite development server...' && npm run dev; exec bash"
    else
        echo "Could not find a suitable terminal emulator. Please start the frontend server manually."
        echo "cd '$PROJECT_ROOT/frontend' && npm run dev"
    fi
fi

echo
echo "==================================================="
echo "Development servers are starting in separate windows."
echo
echo "Frontend will be available at: http://localhost:5173"
echo "Backend API will be available at: http://localhost:5000"
echo
echo "Default admin credentials:"
echo "- Employee Number: ADMIN001"
echo "- Password: admin123"
echo "==================================================="
echo
