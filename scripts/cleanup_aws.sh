#!/bin/bash

# SupplyLine MRO Suite - AWS Cleanup Script
# This script safely removes all existing AWS resources to prepare for fresh deployment

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check if AWS CLI is configured
check_aws_cli() {
    log_info "Checking AWS CLI configuration..."
    
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS CLI is not configured or credentials are invalid"
        exit 1
    fi
    
    log_success "AWS CLI is properly configured"
}

# List existing resources
list_existing_resources() {
    log_info "Scanning for existing SupplyLine resources..."
    
    echo "CloudFormation Stacks:"
    aws cloudformation list-stacks \
        --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE ROLLBACK_COMPLETE \
        --query 'StackSummaries[?contains(StackName, `supplyline`) || contains(StackName, `SupplyLine`)].{Name:StackName,Status:StackStatus,Created:CreationTime}' \
        --output table
    
    echo ""
    echo "ECR Repositories:"
    aws ecr describe-repositories \
        --query 'repositories[?contains(repositoryName, `supplyline`) || contains(repositoryName, `SupplyLine`)].{Name:repositoryName,Created:createdAt}' \
        --output table 2>/dev/null || echo "No ECR repositories found"
    
    echo ""
    echo "ECS Clusters:"
    aws ecs list-clusters \
        --query 'clusterArns[?contains(@, `supplyline`) || contains(@, `SupplyLine`)]' \
        --output table 2>/dev/null || echo "No ECS clusters found"
}

# Delete CloudFormation stacks
delete_cloudformation_stacks() {
    log_info "Deleting CloudFormation stacks..."
    
    # Get all SupplyLine stacks
    STACKS=$(aws cloudformation list-stacks \
        --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE ROLLBACK_COMPLETE \
        --query 'StackSummaries[?contains(StackName, `supplyline`) || contains(StackName, `SupplyLine`)].StackName' \
        --output text)
    
    if [ -z "$STACKS" ]; then
        log_info "No CloudFormation stacks found to delete"
        return 0
    fi
    
    # Delete application stacks first (they depend on infrastructure)
    for stack in $STACKS; do
        if [[ $stack == *"application"* ]]; then
            log_info "Deleting application stack: $stack"
            aws cloudformation delete-stack --stack-name $stack --region $AWS_REGION
            
            log_info "Waiting for stack deletion to complete: $stack"
            aws cloudformation wait stack-delete-complete --stack-name $stack --region $AWS_REGION
            log_success "Application stack deleted: $stack"
        fi
    done
    
    # Then delete infrastructure stacks
    for stack in $STACKS; do
        if [[ $stack == *"infrastructure"* ]]; then
            log_info "Deleting infrastructure stack: $stack"
            aws cloudformation delete-stack --stack-name $stack --region $AWS_REGION
            
            log_info "Waiting for stack deletion to complete: $stack"
            aws cloudformation wait stack-delete-complete --stack-name $stack --region $AWS_REGION
            log_success "Infrastructure stack deleted: $stack"
        fi
    done
    
    # Delete any remaining stacks
    for stack in $STACKS; do
        if [[ $stack != *"application"* ]] && [[ $stack != *"infrastructure"* ]]; then
            log_info "Deleting remaining stack: $stack"
            aws cloudformation delete-stack --stack-name $stack --region $AWS_REGION
            
            log_info "Waiting for stack deletion to complete: $stack"
            aws cloudformation wait stack-delete-complete --stack-name $stack --region $AWS_REGION
            log_success "Stack deleted: $stack"
        fi
    done
}

# Delete ECR repositories
delete_ecr_repositories() {
    log_info "Deleting ECR repositories..."
    
    # Get all SupplyLine ECR repositories
    REPOS=$(aws ecr describe-repositories \
        --query 'repositories[?contains(repositoryName, `supplyline`) || contains(repositoryName, `SupplyLine`)].repositoryName' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$REPOS" ]; then
        log_info "No ECR repositories found to delete"
        return 0
    fi
    
    for repo in $REPOS; do
        log_info "Deleting ECR repository: $repo"
        
        # Delete all images first
        aws ecr list-images --repository-name $repo --query 'imageIds[*]' --output json > /tmp/images.json 2>/dev/null || echo "[]" > /tmp/images.json
        
        if [ -s /tmp/images.json ] && [ "$(cat /tmp/images.json)" != "[]" ]; then
            log_info "Deleting images in repository: $repo"
            aws ecr batch-delete-image --repository-name $repo --image-ids file:///tmp/images.json
        fi
        
        # Delete the repository
        aws ecr delete-repository --repository-name $repo --force
        log_success "ECR repository deleted: $repo"
    done
    
    # Clean up temp file
    rm -f /tmp/images.json
}

# Clean up orphaned ECS resources
cleanup_ecs_resources() {
    log_info "Cleaning up orphaned ECS resources..."
    
    # Get all SupplyLine ECS clusters
    CLUSTERS=$(aws ecs list-clusters \
        --query 'clusterArns[?contains(@, `supplyline`) || contains(@, `SupplyLine`)]' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$CLUSTERS" ]; then
        log_info "No ECS clusters found to clean up"
        return 0
    fi
    
    for cluster in $CLUSTERS; do
        cluster_name=$(basename $cluster)
        log_info "Cleaning up ECS cluster: $cluster_name"
        
        # Stop all services in the cluster
        SERVICES=$(aws ecs list-services --cluster $cluster_name --query 'serviceArns' --output text 2>/dev/null || echo "")
        
        for service in $SERVICES; do
            if [ "$service" != "None" ] && [ ! -z "$service" ]; then
                service_name=$(basename $service)
                log_info "Stopping ECS service: $service_name"
                aws ecs update-service --cluster $cluster_name --service $service_name --desired-count 0
                aws ecs delete-service --cluster $cluster_name --service $service_name --force
            fi
        done
        
        # Delete the cluster
        aws ecs delete-cluster --cluster $cluster_name
        log_success "ECS cluster deleted: $cluster_name"
    done
}

# Verify cleanup
verify_cleanup() {
    log_info "Verifying cleanup completion..."
    
    # Check CloudFormation stacks
    REMAINING_STACKS=$(aws cloudformation list-stacks \
        --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE ROLLBACK_COMPLETE \
        --query 'StackSummaries[?contains(StackName, `supplyline`) || contains(StackName, `SupplyLine`)].StackName' \
        --output text)
    
    if [ ! -z "$REMAINING_STACKS" ]; then
        log_warning "Some CloudFormation stacks still exist: $REMAINING_STACKS"
    else
        log_success "All CloudFormation stacks cleaned up"
    fi
    
    # Check ECR repositories
    REMAINING_REPOS=$(aws ecr describe-repositories \
        --query 'repositories[?contains(repositoryName, `supplyline`) || contains(repositoryName, `SupplyLine`)].repositoryName' \
        --output text 2>/dev/null || echo "")
    
    if [ ! -z "$REMAINING_REPOS" ]; then
        log_warning "Some ECR repositories still exist: $REMAINING_REPOS"
    else
        log_success "All ECR repositories cleaned up"
    fi
    
    # Check ECS clusters
    REMAINING_CLUSTERS=$(aws ecs list-clusters \
        --query 'clusterArns[?contains(@, `supplyline`) || contains(@, `SupplyLine`)]' \
        --output text 2>/dev/null || echo "")
    
    if [ ! -z "$REMAINING_CLUSTERS" ]; then
        log_warning "Some ECS clusters still exist: $REMAINING_CLUSTERS"
    else
        log_success "All ECS clusters cleaned up"
    fi
}

# Main cleanup process
main() {
    log_info "Starting SupplyLine MRO Suite AWS cleanup..."
    echo "=================================================="
    
    # Confirm with user
    echo ""
    log_warning "This will DELETE all existing SupplyLine AWS resources!"
    log_warning "This includes:"
    log_warning "- CloudFormation stacks (infrastructure and applications)"
    log_warning "- ECR repositories and container images"
    log_warning "- ECS clusters and services"
    log_warning "- RDS databases (with final snapshots)"
    log_warning "- Load balancers and networking resources"
    echo ""
    
    read -p "Are you sure you want to proceed? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Cleanup cancelled by user"
        exit 0
    fi
    
    echo ""
    log_info "Proceeding with cleanup..."
    
    # Run cleanup steps
    check_aws_cli
    list_existing_resources
    
    echo ""
    log_info "Starting resource deletion..."
    
    delete_cloudformation_stacks
    delete_ecr_repositories
    cleanup_ecs_resources
    
    echo ""
    verify_cleanup
    
    echo ""
    log_success "AWS cleanup completed!"
    log_info "You can now run a fresh deployment with: ./scripts/deploy.sh"
}

# Run main function
main "$@"
