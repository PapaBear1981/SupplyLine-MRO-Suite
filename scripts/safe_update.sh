#!/bin/bash
# Safe Update Script for SupplyLine MRO Suite
# This script updates the application while preserving the database

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./database/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="pre_update_${TIMESTAMP}.db"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SupplyLine MRO Suite - Safe Update Script             ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Step 1: Create a backup of the database
print_status "Creating database backup..."

if [ -f "./database/tools.db" ]; then
    cp "./database/tools.db" "${BACKUP_DIR}/${BACKUP_NAME}"
    print_success "Database backed up to: ${BACKUP_DIR}/${BACKUP_NAME}"
else
    print_warning "Database file not found at ./database/tools.db"
    print_warning "This might be a fresh installation or database is in Docker volume"
fi

# Step 2: Pull latest changes (if in git repo)
if [ -d ".git" ]; then
    print_status "Pulling latest changes from git..."
    git pull || print_warning "Git pull failed or no changes to pull"
fi

# Step 3: Build new images
print_status "Building new Docker images..."
docker-compose build --no-cache

# Step 4: Stop containers (but keep volumes!)
print_status "Stopping containers (preserving volumes)..."
docker-compose stop

# Step 5: Start updated containers
print_status "Starting updated containers..."
docker-compose up -d

# Step 6: Wait for services to be healthy
print_status "Waiting for services to start..."
sleep 5

# Check backend health
print_status "Checking backend health..."
for i in {1..30}; do
    if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend health check failed after 30 attempts"
        print_warning "Check logs with: docker-compose logs backend"
        exit 1
    fi
    sleep 2
done

# Check frontend health
print_status "Checking frontend health..."
for i in {1..30}; do
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        print_success "Frontend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Frontend health check failed after 30 attempts"
        print_warning "Check logs with: docker-compose logs frontend"
        exit 1
    fi
    sleep 2
done

# Step 7: Clean up old images
print_status "Cleaning up old Docker images..."
docker image prune -f

# Step 8: Show running containers
print_status "Current running containers:"
docker-compose ps

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Update completed successfully!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Application URLs:${NC}"
echo -e "  Frontend: ${GREEN}http://localhost${NC}"
echo -e "  Backend:  ${GREEN}http://localhost:5000${NC}"
echo ""
echo -e "${BLUE}Backup Location:${NC}"
echo -e "  ${BACKUP_DIR}/${BACKUP_NAME}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  View logs:        ${BLUE}docker-compose logs -f${NC}"
echo -e "  Restart services: ${BLUE}docker-compose restart${NC}"
echo -e "  Stop services:    ${BLUE}docker-compose stop${NC}"
echo ""

