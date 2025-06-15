#!/bin/bash

# Debug script for Cloud Run deployment issues
# This script helps diagnose common deployment problems

set -e

echo "🔍 SupplyLine MRO Suite - Deployment Debug Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${PROJECT_ID:-"gen-lang-client-0819985982"}
REGION=${REGION:-"us-west1"}
ENVIRONMENT=${ENVIRONMENT:-"supplyline-beta"}

echo -e "${BLUE}Project ID:${NC} $PROJECT_ID"
echo -e "${BLUE}Region:${NC} $REGION"
echo -e "${BLUE}Environment:${NC} $ENVIRONMENT"
echo ""

# Function to check service status
check_service() {
    local service_name=$1
    echo -e "${BLUE}Checking $service_name...${NC}"
    
    # Get service URL
    local url=$(gcloud run services describe "$service_name" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$url" = "NOT_FOUND" ]; then
        echo -e "${RED}❌ Service $service_name not found${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Service URL: $url${NC}"
    
    # Test health endpoint for backend
    if [[ "$service_name" == *"backend"* ]]; then
        echo "Testing health endpoint..."
        local health_response=$(curl -s "$url/api/health" || echo "CURL_FAILED")
        if [ "$health_response" = "CURL_FAILED" ]; then
            echo -e "${RED}❌ Health check failed - curl error${NC}"
        else
            echo -e "${YELLOW}Health response: $health_response${NC}"
        fi
    fi
    
    # Test basic connectivity for frontend
    if [[ "$service_name" == *"frontend"* ]]; then
        echo "Testing frontend connectivity..."
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "CURL_FAILED")
        if [ "$status_code" = "200" ]; then
            echo -e "${GREEN}✅ Frontend responding (HTTP $status_code)${NC}"
        else
            echo -e "${RED}❌ Frontend not responding (HTTP $status_code)${NC}"
        fi
    fi
    
    echo ""
}

# Function to check Cloud SQL
check_cloud_sql() {
    echo -e "${BLUE}Checking Cloud SQL instance...${NC}"
    
    local instance_name="supplyline-db"
    local status=$(gcloud sql instances describe "$instance_name" --format="value(state)" 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$status" = "NOT_FOUND" ]; then
        echo -e "${RED}❌ Cloud SQL instance $instance_name not found${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Cloud SQL instance status: $status${NC}"
    
    # Check if instance is running
    if [ "$status" != "RUNNABLE" ]; then
        echo -e "${YELLOW}⚠️  Instance is not in RUNNABLE state${NC}"
    fi
    
    echo ""
}

# Function to check secrets
check_secrets() {
    echo -e "${BLUE}Checking secrets...${NC}"
    
    local secrets=("supplyline-secret-key" "supplyline-db-password")
    
    for secret in "${secrets[@]}"; do
        local exists=$(gcloud secrets describe "$secret" --format="value(name)" 2>/dev/null || echo "NOT_FOUND")
        if [ "$exists" = "NOT_FOUND" ]; then
            echo -e "${RED}❌ Secret $secret not found${NC}"
        else
            echo -e "${GREEN}✅ Secret $secret exists${NC}"
        fi
    done
    
    echo ""
}

# Function to get service logs
get_service_logs() {
    local service_name=$1
    echo -e "${BLUE}Getting recent logs for $service_name...${NC}"
    
    echo "Recent logs (last 10 entries):"
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$service_name" \
        --limit=10 \
        --format="table(timestamp,severity,textPayload)" \
        --project="$PROJECT_ID" 2>/dev/null || echo "No logs found or logging not accessible"
    
    echo ""
}

# Main execution
echo "1. Checking Cloud SQL..."
check_cloud_sql

echo "2. Checking secrets..."
check_secrets

echo "3. Checking backend service..."
check_service "supplyline-backend-$ENVIRONMENT"

echo "4. Checking frontend service..."
check_service "supplyline-frontend-$ENVIRONMENT"

echo "5. Getting backend logs..."
get_service_logs "supplyline-backend-$ENVIRONMENT"

echo "6. Getting frontend logs..."
get_service_logs "supplyline-frontend-$ENVIRONMENT"

echo -e "${GREEN}Debug script completed!${NC}"
echo ""
echo "Common issues and solutions:"
echo "- If backend health check fails: Check Cloud SQL connectivity and secrets"
echo "- If CORS errors occur: Verify frontend and backend URLs match"
echo "- If services not found: Check if deployment completed successfully"
echo "- For detailed logs: Use 'gcloud logging read' with specific filters"
