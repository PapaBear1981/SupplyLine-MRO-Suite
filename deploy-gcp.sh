#!/bin/bash

# SupplyLine MRO Suite - Google Cloud Platform Deployment Script
# This script deploys the application to Google Cloud Run

set -euo pipefail  # Fail fast, catch pipe errors & unset vars

# Configuration
PROJECT_ID=${PROJECT_ID:-"gen-lang-client-0819985982"}
REGION=${REGION:-"us-west1"}
ENVIRONMENT=${ENVIRONMENT:-"supplyline-beta"}
SECRET_KEY=${SECRET_KEY:-"$(openssl rand -base64 32)"}
DB_PASSWORD=${DB_PASSWORD:-"$(openssl rand -base64 24)"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"$(openssl rand -base64 16)"}
CONNECTOR_NAME=${CONNECTOR_NAME:-"supplyline-connector"}
VPC_NETWORK=${VPC_NETWORK:-"default"}
VPC_RANGE=${VPC_RANGE:-"10.8.0.0/28"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with gcloud. Please run 'gcloud auth login'"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Set up Google Cloud project
setup_project() {
    log_info "Setting up Google Cloud project..."
    
    # Set the project
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    log_info "Enabling required APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable sqladmin.googleapis.com
    gcloud services enable secretmanager.googleapis.com
    gcloud services enable vpcaccess.googleapis.com
    
    log_success "Project setup completed"
}

# Create secrets
create_secrets() {
    log_info "Creating secrets..."
    
    # Create secret key if it doesn't exist
    if ! gcloud secrets describe supplyline-secret-key >/dev/null 2>&1; then
        echo -n "$SECRET_KEY" | gcloud secrets create supplyline-secret-key --replication-policy="automatic" --data-file=-
    fi

    # Create database credentials if they don't exist (you'll need to update these)
    if ! gcloud secrets describe supplyline-db-username >/dev/null 2>&1; then
        echo -n "supplyline_user" | gcloud secrets create supplyline-db-username --replication-policy="automatic" --data-file=-
    fi

    if ! gcloud secrets describe supplyline-db-password >/dev/null 2>&1; then
        echo -n "$DB_PASSWORD" | gcloud secrets create supplyline-db-password --replication-policy="automatic" --data-file=-
    fi
    
    log_success "Secrets created"
}

# Create service accounts for Cloud Run
create_service_accounts() {
    log_info "Creating service accounts..."

    if ! gcloud iam service-accounts describe supplyline-backend-sa@${PROJECT_ID}.iam.gserviceaccount.com >/dev/null 2>&1; then
        gcloud iam service-accounts create supplyline-backend-sa --display-name "SupplyLine Backend Service Account"
    fi

    if ! gcloud iam service-accounts describe supplyline-frontend-sa@${PROJECT_ID}.iam.gserviceaccount.com >/dev/null 2>&1; then
        gcloud iam service-accounts create supplyline-frontend-sa --display-name "SupplyLine Frontend Service Account"
    fi

    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:supplyline-backend-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/run.serviceAgent" || true

    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:supplyline-backend-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/cloudsql.client" || true

    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:supplyline-frontend-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/run.serviceAgent" || true

    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:supplyline-frontend-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/cloudsql.client" || true

    log_success "Service accounts configured"
}

# Create VPC Access connector for Cloud Run
create_vpc_connector() {
    log_info "Configuring VPC Access connector..."

    if ! gcloud compute networks vpc-access connectors describe $CONNECTOR_NAME --region=$REGION >/dev/null 2>&1; then
        gcloud compute networks vpc-access connectors create $CONNECTOR_NAME \
            --region=$REGION \
            --network=$VPC_NETWORK \
            --range=$VPC_RANGE
    else
        log_warning "VPC connector already exists"
    fi

    log_success "VPC Access connector ready"
}

# Create Cloud SQL instance
create_database() {
    log_info "Creating Cloud SQL instance..."
    
    # Create PostgreSQL instance
    gcloud sql instances create supplyline-db \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=$REGION \
        --storage-type=SSD \
        --storage-size=10 \
        --backup-start-time=03:00 \
        --enable-bin-log \
        --deletion-protection || log_warning "Database instance may already exist"
    
    # Create database
    gcloud sql databases create supplyline --instance=supplyline-db || log_warning "Database may already exist"
    
    # Create user
    gcloud sql users create supplyline_user --instance=supplyline-db --password="$DB_PASSWORD" || log_warning "User may already exist"
    
    log_success "Database setup completed"
}

# Deploy using Cloud Build
deploy_application() {
    log_info "Deploying application using Cloud Build..."
    
    # Submit build
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions=_ENVIRONMENT=$ENVIRONMENT,_REGION=$REGION,_CLOUDSQL_INSTANCE=$PROJECT_ID:$REGION:supplyline-db \
        .
    
    log_success "Application deployed successfully"
}

# Get service URLs
get_service_urls() {
    log_info "Getting service URLs..."
    
    BACKEND_URL=$(gcloud run services describe supplyline-backend-$ENVIRONMENT --region=$REGION --format="value(status.url)")
    FRONTEND_URL=$(gcloud run services describe supplyline-frontend-$ENVIRONMENT --region=$REGION --format="value(status.url)")
    
    log_success "Deployment completed!"
    echo ""
    echo "Service URLs:"
    echo "Frontend: $FRONTEND_URL"
    echo "Backend:  $BACKEND_URL"
    echo ""
    echo "Admin credentials:"
    echo "Username: ADMIN001"
    echo "Password: $ADMIN_PASSWORD"
    echo ""
    echo "⚠️  IMPORTANT: Save these credentials securely!"
    echo "⚠️  Change the admin password after first login!"
}

# Main deployment flow
main() {
    log_info "Starting SupplyLine MRO Suite deployment to Google Cloud Platform"
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Environment: $ENVIRONMENT"
    echo ""
    
    check_prerequisites
    setup_project
    create_service_accounts
    create_vpc_connector
    create_secrets
    create_database
    deploy_application
    get_service_urls
    
    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"
