#!/bin/bash

echo "========================================"
echo " SupplyLine MRO Suite - Portable PWA"
echo "========================================"
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    echo
    echo "Please install Node.js from: https://nodejs.org/"
    echo
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo

# Install dependencies if needed
if [ ! -d "server/node_modules" ]; then
    echo "📦 Installing server dependencies..."
    cd server
    npm install
    cd ..
    echo
fi

echo "🚀 Starting SupplyLine MRO Suite PWA Server..."
echo
npm start