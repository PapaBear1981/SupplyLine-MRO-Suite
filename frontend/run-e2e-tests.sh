#!/bin/bash

# E2E Test Runner Script for SupplyLine MRO Suite
# This script sets up the environment and runs Playwright E2E tests

set -e  # Exit on any error

echo "🚀 Starting E2E Test Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the frontend directory"
    exit 1
fi

# Check if Playwright is installed
if ! command -v npx &> /dev/null; then
    print_error "npx not found. Please install Node.js"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
fi

# Install Playwright browsers if not already installed
print_status "Checking Playwright browsers..."
npx playwright install --with-deps

# Check if backend is running
print_status "Checking backend server..."
if curl -f http://localhost:5000/api/health &> /dev/null; then
    print_status "Backend server is running"
else
    print_warning "Backend server is not running on http://localhost:5000"
    print_warning "Please start the backend server before running tests"
    echo "To start the backend:"
    echo "  cd ../backend"
    echo "  python app.py"
    exit 1
fi

# Check if frontend is running (for dev mode)
print_status "Checking frontend server..."
if curl -f http://localhost:5173 &> /dev/null; then
    print_status "Frontend dev server is running"
    export PLAYWRIGHT_BASE_URL="http://localhost:5173"
elif curl -f http://localhost:4173 &> /dev/null; then
    print_status "Frontend preview server is running"
    export PLAYWRIGHT_BASE_URL="http://localhost:4173"
else
    print_warning "Frontend server is not running"
    print_status "Starting frontend preview server..."
    
    # Build the frontend if dist doesn't exist
    if [ ! -d "dist" ]; then
        print_status "Building frontend..."
        npm run build
    fi
    
    # Start preview server in background
    npm run preview &
    FRONTEND_PID=$!
    
    # Wait for server to start
    print_status "Waiting for frontend server to start..."
    for i in {1..30}; do
        if curl -f http://localhost:4173 &> /dev/null; then
            print_status "Frontend preview server started"
            export PLAYWRIGHT_BASE_URL="http://localhost:4173"
            break
        fi
        sleep 1
    done
    
    if [ $i -eq 30 ]; then
        print_error "Frontend server failed to start"
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
fi

# Parse command line arguments
BROWSER=""
UI_MODE=false
DEBUG_MODE=false
HEADED=false
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --ui)
            UI_MODE=true
            shift
            ;;
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        --headed)
            HEADED=true
            shift
            ;;
        --test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--browser chromium|firefox|webkit] [--ui] [--debug] [--headed] [--test test-file]"
            exit 1
            ;;
    esac
done

# Build the Playwright command
PLAYWRIGHT_CMD="npx playwright test"

if [ ! -z "$BROWSER" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --project=$BROWSER"
fi

if [ "$UI_MODE" = true ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --ui"
elif [ "$DEBUG_MODE" = true ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --debug"
elif [ "$HEADED" = true ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --headed"
fi

if [ ! -z "$SPECIFIC_TEST" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD $SPECIFIC_TEST"
fi

# Run the tests
print_status "Running E2E tests..."
echo "Command: $PLAYWRIGHT_CMD"
echo "Base URL: $PLAYWRIGHT_BASE_URL"
echo ""

$PLAYWRIGHT_CMD

TEST_EXIT_CODE=$?

# Cleanup
if [ ! -z "$FRONTEND_PID" ]; then
    print_status "Stopping frontend preview server..."
    kill $FRONTEND_PID 2>/dev/null || true
fi

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_status "All tests passed! 🎉"
else
    print_error "Some tests failed"
fi

print_status "Test reports available at:"
echo "  - HTML Report: playwright-report/index.html"
echo "  - Test Results: test-results/"

exit $TEST_EXIT_CODE
