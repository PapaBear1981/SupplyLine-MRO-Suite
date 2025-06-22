#!/bin/bash

# SupplyLine MRO Suite Deployment Script
# This script deploys the application to AWS using CloudFormation and ECR

set -e

# Configuration
STACK_NAME="supplyline-mro-suite"
INFRASTRUCTURE_STACK="${STACK_NAME}-infrastructure"
APPLICATION_STACK="${STACK_NAME}-application"
AWS_REGION="us-east-1"
ECR_REPOSITORY="supplyline-backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_error "jq is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

create_ecr_repository() {
    log_info "Creating ECR repository if it doesn't exist..."
    
    if ! aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &> /dev/null; then
        aws ecr create-repository \
            --repository-name $ECR_REPOSITORY \
            --region $AWS_REGION \
            --image-scanning-configuration scanOnPush=true
        log_success "ECR repository created: $ECR_REPOSITORY"
    else
        log_info "ECR repository already exists: $ECR_REPOSITORY"
    fi
}

build_and_push_backend() {
    log_info "Building and pushing backend Docker image..."
    
    # Get ECR login token
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Build Docker image
    cd backend
    docker build -t $ECR_REPOSITORY:latest .
    
    # Tag image for ECR
    ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
    docker tag $ECR_REPOSITORY:latest $ECR_URI
    
    # Push image to ECR
    docker push $ECR_URI
    
    cd ..
    log_success "Backend image pushed to ECR: $ECR_URI"
    echo $ECR_URI
}

deploy_infrastructure() {
    log_info "Deploying infrastructure stack..."
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $INFRASTRUCTURE_STACK --region $AWS_REGION &> /dev/null; then
        log_info "Updating existing infrastructure stack..."
        aws cloudformation update-stack \
            --stack-name $INFRASTRUCTURE_STACK \
            --template-body file://aws/cloudformation/infrastructure.yaml \
            --parameters ParameterKey=Environment,ParameterValue=production \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION
    else
        log_info "Creating new infrastructure stack..."
        aws cloudformation create-stack \
            --stack-name $INFRASTRUCTURE_STACK \
            --template-body file://aws/cloudformation/infrastructure.yaml \
            --parameters ParameterKey=Environment,ParameterValue=production \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION
    fi
    
    log_info "Waiting for infrastructure stack to complete..."
    aws cloudformation wait stack-create-complete --stack-name $INFRASTRUCTURE_STACK --region $AWS_REGION || \
    aws cloudformation wait stack-update-complete --stack-name $INFRASTRUCTURE_STACK --region $AWS_REGION
    
    log_success "Infrastructure stack deployed successfully"
}

deploy_application() {
    local backend_image_uri=$1
    
    log_info "Deploying application stack..."
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $APPLICATION_STACK --region $AWS_REGION &> /dev/null; then
        log_info "Updating existing application stack..."
        aws cloudformation update-stack \
            --stack-name $APPLICATION_STACK \
            --template-body file://aws/cloudformation/application.yaml \
            --parameters \
                ParameterKey=InfrastructureStackName,ParameterValue=$INFRASTRUCTURE_STACK \
                ParameterKey=Environment,ParameterValue=production \
                ParameterKey=BackendImageUri,ParameterValue=$backend_image_uri \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION
    else
        log_info "Creating new application stack..."
        aws cloudformation create-stack \
            --stack-name $APPLICATION_STACK \
            --template-body file://aws/cloudformation/application.yaml \
            --parameters \
                ParameterKey=InfrastructureStackName,ParameterValue=$INFRASTRUCTURE_STACK \
                ParameterKey=Environment,ParameterValue=production \
                ParameterKey=BackendImageUri,ParameterValue=$backend_image_uri \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION
    fi
    
    log_info "Waiting for application stack to complete..."
    aws cloudformation wait stack-create-complete --stack-name $APPLICATION_STACK --region $AWS_REGION || \
    aws cloudformation wait stack-update-complete --stack-name $APPLICATION_STACK --region $AWS_REGION
    
    log_success "Application stack deployed successfully"
}

build_and_deploy_frontend() {
    log_info "Building and deploying frontend..."
    
    # Get S3 bucket name from CloudFormation output
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name $INFRASTRUCTURE_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
        --output text)
    
    if [ -z "$S3_BUCKET" ]; then
        log_error "Could not retrieve S3 bucket name from infrastructure stack"
        exit 1
    fi
    
    # Get ALB DNS name for API URL
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    # Build frontend
    cd frontend
    npm ci
    VITE_API_URL="https://$ALB_DNS/api" npm run build
    
    # Deploy to S3
    aws s3 sync dist/ s3://$S3_BUCKET --delete
    
    # Get CloudFront distribution ID and invalidate cache
    CLOUDFRONT_ID=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
        --output text)
    
    if [ ! -z "$CLOUDFRONT_ID" ]; then
        aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
    fi
    
    cd ..
    log_success "Frontend deployed to S3 bucket: $S3_BUCKET"
}

show_deployment_info() {
    log_info "Deployment completed! Here are the details:"
    
    # Get CloudFront domain
    CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
        --output text)
    
    # Get ALB DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    echo ""
    echo "🌐 Frontend URL: https://$CLOUDFRONT_DOMAIN"
    echo "🔗 Backend API: https://$ALB_DNS/api"
    echo "📊 AWS Console: https://console.aws.amazon.com/cloudformation/home?region=$AWS_REGION"
    echo ""
    log_success "Deployment completed successfully!"
}

# Main deployment process
main() {
    log_info "Starting SupplyLine MRO Suite deployment..."
    
    check_prerequisites
    create_ecr_repository
    
    # Build and push backend
    backend_image_uri=$(build_and_push_backend)
    
    # Deploy infrastructure
    deploy_infrastructure
    
    # Deploy application
    deploy_application $backend_image_uri
    
    # Build and deploy frontend
    build_and_deploy_frontend
    
    # Show deployment information
    show_deployment_info
}

# Run main function
main "$@"
