#!/bin/bash

# SupplyLine MRO Suite - AWS Deployment Validation Script
# This script validates that the AWS deployment is working correctly

set -e

# Configuration
STACK_NAME_PREFIX="supplyline-mro-suite"
INFRASTRUCTURE_STACK="${STACK_NAME_PREFIX}-infrastructure"
APPLICATION_STACK="${STACK_NAME_PREFIX}-application"
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

# Check CloudFormation stacks
check_cloudformation_stacks() {
    log_info "Checking CloudFormation stacks..."
    
    # Check infrastructure stack
    if aws cloudformation describe-stacks --stack-name $INFRASTRUCTURE_STACK --region $AWS_REGION &> /dev/null; then
        INFRA_STATUS=$(aws cloudformation describe-stacks --stack-name $INFRASTRUCTURE_STACK --region $AWS_REGION --query 'Stacks[0].StackStatus' --output text)
        if [ "$INFRA_STATUS" = "CREATE_COMPLETE" ] || [ "$INFRA_STATUS" = "UPDATE_COMPLETE" ]; then
            log_success "Infrastructure stack is healthy: $INFRA_STATUS"
        else
            log_error "Infrastructure stack is in bad state: $INFRA_STATUS"
            return 1
        fi
    else
        log_error "Infrastructure stack not found"
        return 1
    fi
    
    # Check application stack
    if aws cloudformation describe-stacks --stack-name $APPLICATION_STACK --region $AWS_REGION &> /dev/null; then
        APP_STATUS=$(aws cloudformation describe-stacks --stack-name $APPLICATION_STACK --region $AWS_REGION --query 'Stacks[0].StackStatus' --output text)
        if [ "$APP_STATUS" = "CREATE_COMPLETE" ] || [ "$APP_STATUS" = "UPDATE_COMPLETE" ]; then
            log_success "Application stack is healthy: $APP_STATUS"
        else
            log_error "Application stack is in bad state: $APP_STATUS"
            return 1
        fi
    else
        log_error "Application stack not found"
        return 1
    fi
}

# Check RDS database
check_database() {
    log_info "Checking RDS database..."
    
    DB_IDENTIFIER=$(aws cloudformation describe-stacks \
        --stack-name $INFRASTRUCTURE_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`DatabaseIdentifier`].OutputValue' \
        --output text)
    
    if [ -z "$DB_IDENTIFIER" ] || [ "$DB_IDENTIFIER" = "None" ]; then
        log_error "Could not get database identifier from CloudFormation"
        return 1
    fi
    
    DB_STATUS=$(aws rds describe-db-instances \
        --db-instance-identifier $DB_IDENTIFIER \
        --region $AWS_REGION \
        --query 'DBInstances[0].DBInstanceStatus' \
        --output text)
    
    if [ "$DB_STATUS" = "available" ]; then
        log_success "Database is available"
    else
        log_error "Database is not available: $DB_STATUS"
        return 1
    fi
}

# Check ECS service
check_ecs_service() {
    log_info "Checking ECS service..."
    
    CLUSTER_NAME=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' \
        --output text)
    
    SERVICE_NAME=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ServiceName`].OutputValue' \
        --output text)
    
    if [ -z "$CLUSTER_NAME" ] || [ "$SERVICE_NAME" = "None" ]; then
        log_error "Could not get ECS cluster/service info from CloudFormation"
        return 1
    fi
    
    SERVICE_STATUS=$(aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION \
        --query 'services[0].status' \
        --output text)
    
    RUNNING_COUNT=$(aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION \
        --query 'services[0].runningCount' \
        --output text)
    
    DESIRED_COUNT=$(aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION \
        --query 'services[0].desiredCount' \
        --output text)
    
    if [ "$SERVICE_STATUS" = "ACTIVE" ] && [ "$RUNNING_COUNT" = "$DESIRED_COUNT" ]; then
        log_success "ECS service is healthy: $RUNNING_COUNT/$DESIRED_COUNT tasks running"
    else
        log_error "ECS service is not healthy: Status=$SERVICE_STATUS, Running=$RUNNING_COUNT, Desired=$DESIRED_COUNT"
        return 1
    fi
}

# Check application load balancer
check_load_balancer() {
    log_info "Checking Application Load Balancer..."
    
    ALB_ARN=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerArn`].OutputValue' \
        --output text)
    
    if [ -z "$ALB_ARN" ] || [ "$ALB_ARN" = "None" ]; then
        log_error "Could not get load balancer ARN from CloudFormation"
        return 1
    fi
    
    ALB_STATE=$(aws elbv2 describe-load-balancers \
        --load-balancer-arns $ALB_ARN \
        --region $AWS_REGION \
        --query 'LoadBalancers[0].State.Code' \
        --output text)
    
    if [ "$ALB_STATE" = "active" ]; then
        log_success "Load balancer is active"
    else
        log_error "Load balancer is not active: $ALB_STATE"
        return 1
    fi
}

# Test application endpoints
test_application_endpoints() {
    log_info "Testing application endpoints..."
    
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    if [ -z "$ALB_DNS" ] || [ "$ALB_DNS" = "None" ]; then
        log_error "Could not get load balancer DNS from CloudFormation"
        return 1
    fi
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    if curl -f -s "http://$ALB_DNS/api/health" > /dev/null; then
        log_success "Health endpoint is responding"
    else
        log_error "Health endpoint is not responding"
        return 1
    fi
    
    # Test frontend
    log_info "Testing frontend..."
    if curl -f -s "http://$ALB_DNS/" > /dev/null; then
        log_success "Frontend is responding"
    else
        log_error "Frontend is not responding"
        return 1
    fi
}

# Show deployment information
show_deployment_info() {
    log_info "Deployment Information:"
    echo "=========================="
    
    # Get load balancer DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    # Get CloudFront distribution
    CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name $APPLICATION_STACK \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomain`].OutputValue' \
        --output text 2>/dev/null || echo "Not configured")
    
    echo "Application URL: http://$ALB_DNS"
    if [ "$CLOUDFRONT_DOMAIN" != "Not configured" ]; then
        echo "CloudFront URL: https://$CLOUDFRONT_DOMAIN"
    fi
    echo "Health Check: http://$ALB_DNS/api/health"
    echo "Admin Login: ADMIN001 / (check deployment logs for password)"
    echo "=========================="
}

# Main validation process
main() {
    log_info "Starting SupplyLine MRO Suite deployment validation..."
    echo "======================================================"
    
    # Run all checks
    check_aws_cli
    check_cloudformation_stacks
    check_database
    check_ecs_service
    check_load_balancer
    test_application_endpoints
    
    log_success "All validation checks passed!"
    echo ""
    show_deployment_info
}

# Run main function
main "$@"
