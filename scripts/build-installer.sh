#!/bin/bash
# SupplyLine MRO Suite - Build Installer Script for macOS/Linux
# This script automates the entire build process for creating installers

echo "========================================"
echo "SupplyLine MRO Suite - Build Installer"
echo "========================================"
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python from https://python.org/"
    exit 1
fi

echo "Step 1: Installing dependencies..."
echo
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "Step 2: Installing frontend dependencies..."
echo
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install frontend dependencies"
    exit 1
fi
cd ..

echo
echo "Step 3: Installing backend dependencies..."
echo
cd backend
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install backend dependencies"
    exit 1
fi
cd ..

echo
echo "Step 4: Building frontend..."
echo
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build frontend"
    exit 1
fi
cd ..

echo
echo "Step 5: Building Electron application..."
echo

# Detect platform and build accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    npm run dist:mac
    INSTALLER_TYPE="DMG"
    INSTALLER_LOCATION="dist/*.dmg"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    npm run dist:linux
    INSTALLER_TYPE="AppImage and DEB"
    INSTALLER_LOCATION="dist/*.{AppImage,deb}"
else
    echo "Unsupported platform: $OSTYPE"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build Electron application"
    exit 1
fi

echo
echo "========================================"
echo "BUILD COMPLETED SUCCESSFULLY!"
echo "========================================"
echo
echo "Installers created in the 'dist' folder:"
echo "- $INSTALLER_TYPE installer(s)"
echo "- Location: $INSTALLER_LOCATION"
echo
echo "You can now distribute these files for easy installation."
echo
