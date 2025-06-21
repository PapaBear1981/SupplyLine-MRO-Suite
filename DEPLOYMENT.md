# SupplyLine MRO Suite - AWS Deployment Guide

This guide covers deploying the SupplyLine MRO Suite to AWS using modern cloud-native practices.

## Architecture Overview

The application is deployed using the following AWS services:

- **Frontend**: React SPA hosted on S3 + CloudFront CDN
- **Backend**: Flask API running on ECS Fargate with Application Load Balancer
- **Database**: Amazon RDS PostgreSQL
- **Container Registry**: Amazon ECR
- **Secrets Management**: AWS Secrets Manager
- **Infrastructure**: AWS CloudFormation for Infrastructure as Code

## Prerequisites

Before deploying, ensure you have:

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **Docker** installed for building container images

3. **Node.js 18+** for building the frontend

4. **Python 3.11+** for running backend tests

5. **jq** for JSON processing in scripts

6. **AWS Account** with appropriate permissions for:
   - CloudFormation
   - ECS/Fargate
   - RDS
   - S3
   - CloudFront
   - ECR
   - Secrets Manager
   - IAM

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/SupplyLine-MRO-Suite.git
cd SupplyLine-MRO-Suite
```

### 2. Configure Environment Variables

Create a `.env.production` file in the backend directory:

```bash
# Backend Production Environment
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=postgresql://username:password@host:port/database
AWS_REGION=us-east-1
LOG_LEVEL=INFO
```

### 3. Configure GitHub Secrets (for CI/CD)

Add the following secrets to your GitHub repository:

```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=your-frontend-bucket-name
CLOUDFRONT_DISTRIBUTION_ID=your-cloudfront-distribution-id
VITE_API_URL=https://your-api-domain.com/api
SLACK_WEBHOOK=your-slack-webhook-url (optional)
```

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

The application automatically deploys when code is pushed to the `main` or `master` branch.

1. **Push to main branch**:
   ```bash
   git push origin main
   ```

2. **Monitor deployment** in GitHub Actions tab

3. **Access application** at the CloudFront URL provided in the deployment output

### Method 2: Manual Deployment

Use the provided deployment script for manual deployments:

```bash
# Make script executable (Linux/Mac)
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### Method 3: Step-by-Step Manual Deployment

#### Step 1: Deploy Infrastructure

```bash
# Deploy infrastructure stack
aws cloudformation create-stack \
  --stack-name supplyline-mro-suite-infrastructure \
  --template-body file://aws/cloudformation/infrastructure.yaml \
  --parameters ParameterKey=Environment,ParameterValue=production \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name supplyline-mro-suite-infrastructure \
  --region us-east-1
```

#### Step 2: Build and Push Backend Image

```bash
# Create ECR repository
aws ecr create-repository --repository-name supplyline-backend --region us-east-1

# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build and push image
cd backend
docker build -t supplyline-backend .
docker tag supplyline-backend:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/supplyline-backend:latest
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/supplyline-backend:latest
cd ..
```

#### Step 3: Deploy Application

```bash
# Deploy application stack
aws cloudformation create-stack \
  --stack-name supplyline-mro-suite-application \
  --template-body file://aws/cloudformation/application.yaml \
  --parameters \
    ParameterKey=InfrastructureStackName,ParameterValue=supplyline-mro-suite-infrastructure \
    ParameterKey=Environment,ParameterValue=production \
    ParameterKey=BackendImageUri,ParameterValue=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/supplyline-backend:latest \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name supplyline-mro-suite-application \
  --region us-east-1
```

#### Step 4: Build and Deploy Frontend

```bash
# Get S3 bucket name
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name supplyline-mro-suite-infrastructure \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
  --output text)

# Get API URL
ALB_DNS=$(aws cloudformation describe-stacks \
  --stack-name supplyline-mro-suite-application \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text)

# Build frontend
cd frontend
npm ci
VITE_API_URL="https://$ALB_DNS/api" npm run build

# Deploy to S3
aws s3 sync dist/ s3://$S3_BUCKET --delete

# Invalidate CloudFront cache
CLOUDFRONT_ID=$(aws cloudformation describe-stacks \
  --stack-name supplyline-mro-suite-application \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
  --output text)

aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
cd ..
```

## Database Setup

### Initial Database Setup

The application will automatically create database tables on first run. To manually initialize:

```bash
# Connect to the deployed backend container
aws ecs execute-command \
  --cluster supplyline-cluster \
  --task $(aws ecs list-tasks --cluster supplyline-cluster --service supplyline-backend-service --query 'taskArns[0]' --output text) \
  --container backend \
  --interactive \
  --command "/bin/bash"

# Inside the container, run:
python db_init.py
```

### Database Migrations

For database schema changes:

1. Update models in `backend/models.py`
2. Create migration script in `backend/migrations/`
3. Deploy new backend image
4. Run migration in production

## Monitoring and Maintenance

### CloudWatch Logs

- Backend logs: `/ecs/supplyline-mro-suite-application-backend`
- Application metrics available in CloudWatch

### Health Checks

- Backend health: `https://your-alb-dns.com/health`
- Frontend health: Automatic via CloudFront

### Scaling

The ECS service is configured with:
- Minimum 2 tasks
- Maximum 10 tasks (can be adjusted)
- Auto-scaling based on CPU/memory usage

### Backup and Recovery

- RDS automated backups (7-day retention)
- Point-in-time recovery available
- S3 versioning enabled for frontend assets

## Security Considerations

1. **Secrets Management**: All sensitive data stored in AWS Secrets Manager
2. **Network Security**: Private subnets for database, public subnets for load balancer
3. **Encryption**: Data encrypted at rest and in transit
4. **Access Control**: IAM roles with least privilege principle
5. **HTTPS**: Enforced via CloudFront and ALB

## Troubleshooting

### Common Issues

1. **Deployment Fails**:
   - Check CloudFormation events in AWS Console
   - Verify IAM permissions
   - Check CloudWatch logs

2. **Backend Not Responding**:
   - Check ECS service health
   - Review backend logs in CloudWatch
   - Verify database connectivity

3. **Frontend Not Loading**:
   - Check S3 bucket contents
   - Verify CloudFront distribution status
   - Check browser console for errors

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster supplyline-cluster --services supplyline-backend-service

# View recent logs
aws logs tail /ecs/supplyline-mro-suite-application-backend --follow

# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name supplyline-mro-suite-infrastructure

# Update ECS service (force new deployment)
aws ecs update-service --cluster supplyline-cluster --service supplyline-backend-service --force-new-deployment
```

## Cost Optimization

- Use Fargate Spot for non-critical workloads
- Enable S3 Intelligent Tiering
- Set up CloudWatch billing alerts
- Review and optimize RDS instance size based on usage

## Support

For deployment issues:
1. Check this documentation
2. Review CloudWatch logs
3. Check GitHub Issues
4. Contact the development team
