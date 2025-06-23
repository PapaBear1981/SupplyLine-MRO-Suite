# SupplyLine MRO Suite - AWS Deployment Guide

This guide provides step-by-step instructions for deploying the SupplyLine MRO Suite to AWS with robust database handling and error recovery.

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** installed and configured
2. **Docker** installed and running
3. **Git** for version control
4. **Bash** shell (Git Bash on Windows)

### One-Command Deployment

```bash
# Clone and deploy in one go
git clone https://github.com/PapaBear1981/SupplyLine-MRO-Suite.git
cd SupplyLine-MRO-Suite
./scripts/deploy.sh
```

## 📋 Detailed Deployment Steps

### Step 1: Environment Setup

1. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, Region (us-east-1), and output format (json)
   ```

2. **Verify AWS Configuration**
   ```bash
   aws sts get-caller-identity
   ```

3. **Set Environment Variables** (Optional)
   ```bash
   export AWS_REGION=us-east-1
   export DB_PASSWORD=your-secure-password-here
   ```

### Step 2: Deploy Infrastructure

```bash
# Make deployment script executable (Linux/Mac)
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### Step 3: Validate Deployment

```bash
# Run validation script
./scripts/validate_deployment.sh
```

## 🗄️ Database Configuration

### Automatic Database Initialization

The deployment includes robust database initialization that:

- ✅ **Detects Environment**: Automatically switches between SQLite (local) and PostgreSQL (AWS)
- ✅ **Waits for Database**: Retries connection up to 30 times with 5-second intervals
- ✅ **Creates Tables**: Automatically creates all required database tables
- ✅ **Runs Migrations**: Applies all pending database migrations
- ✅ **Creates Admin User**: Generates secure admin credentials
- ✅ **Adds Sample Data**: Creates test tools and chemicals for validation
- ✅ **Health Checks**: Comprehensive database health validation

### Database Features

- **PostgreSQL 15.4** on RDS with encryption
- **Automatic backups** with 7-day retention
- **Performance Insights** enabled
- **Enhanced monitoring** with CloudWatch
- **Connection pooling** optimized for production
- **Auto-scaling storage** (20GB to 100GB)

### Manual Database Operations

If you need to manually initialize or check the database:

```bash
# Get ECS cluster and service info
CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name supplyline-mro-suite-application --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' --output text)
SERVICE_NAME=$(aws cloudformation describe-stacks --stack-name supplyline-mro-suite-application --query 'Stacks[0].Outputs[?OutputKey==`ServiceName`].OutputValue' --output text)

# Get running task
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --desired-status RUNNING --query 'taskArns[0]' --output text)

# Run database health check
aws ecs execute-command --cluster $CLUSTER_NAME --task $TASK_ARN --container backend --interactive --command "python db_health_check.py"

# Initialize database manually (if needed)
aws ecs execute-command --cluster $CLUSTER_NAME --task $TASK_ARN --container backend --interactive --command "python aws_db_init.py"
```

## 🔧 Configuration

### Environment Variables

The application supports extensive configuration through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | Auto-detected |
| `DB_PORT` | PostgreSQL port | 5432 |
| `DB_NAME` | Database name | supplyline |
| `DB_USER` | Database user | supplyline_admin |
| `DB_PASSWORD` | Database password | Auto-generated |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `JWT_SECRET_KEY` | JWT secret key | Auto-generated |
| `CORS_ORIGINS` | Allowed CORS origins | CloudFront domain |

### Security Configuration

- **Encryption at rest** for RDS database
- **SSL/TLS** for all connections
- **VPC isolation** with private subnets
- **Security groups** with minimal required access
- **IAM roles** with least privilege principle
- **Secrets management** through CloudFormation parameters

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudFront    │    │  Application    │    │   RDS PostgreSQL│
│   (Frontend)    │────│  Load Balancer  │────│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   ECS Fargate   │
                       │   (Backend)     │
                       └─────────────────┘
```

### Components

- **CloudFront**: CDN for frontend static files
- **Application Load Balancer**: Routes traffic to backend services
- **ECS Fargate**: Serverless container hosting for backend
- **RDS PostgreSQL**: Managed database with automatic backups
- **VPC**: Isolated network with public/private subnets
- **CloudWatch**: Monitoring and logging

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Timeout**
   ```bash
   # Check database status
   aws rds describe-db-instances --db-instance-identifier supplyline-mro-suite-infrastructure-postgres
   
   # Check security groups
   aws ec2 describe-security-groups --group-names supplyline-mro-suite-infrastructure-DatabaseSecurityGroup
   ```

2. **ECS Service Not Starting**
   ```bash
   # Check service events
   aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME
   
   # Check task logs
   aws logs get-log-events --log-group-name /aws/ecs/supplyline-mro-suite --log-stream-name backend
   ```

3. **Load Balancer Health Checks Failing**
   ```bash
   # Check target group health
   aws elbv2 describe-target-health --target-group-arn $TARGET_GROUP_ARN
   ```

### Database Recovery

If database initialization fails:

1. **Check RDS Status**
   ```bash
   aws rds describe-db-instances --db-instance-identifier supplyline-mro-suite-infrastructure-postgres
   ```

2. **Manual Initialization**
   ```bash
   # Connect to running container and initialize
   aws ecs execute-command --cluster $CLUSTER_NAME --task $TASK_ARN --container backend --interactive --command "python aws_db_init.py"
   ```

3. **Reset Database** (if needed)
   ```bash
   # This will delete and recreate the database - USE WITH CAUTION
   aws rds delete-db-instance --db-instance-identifier supplyline-mro-suite-infrastructure-postgres --skip-final-snapshot
   # Then redeploy the infrastructure stack
   ```

## 📊 Monitoring

### CloudWatch Dashboards

The deployment creates CloudWatch dashboards for:
- **Application Performance**: Response times, error rates
- **Database Metrics**: Connections, CPU, memory usage
- **Infrastructure Health**: ECS tasks, load balancer status

### Alerts

Automatic alerts are configured for:
- High error rates (>5%)
- Database connection issues
- ECS service failures
- Load balancer unhealthy targets

## 🔄 Updates and Maintenance

### Deploying Updates

```bash
# Pull latest changes
git pull origin master

# Redeploy (only updates changed components)
./scripts/deploy.sh
```

### Database Migrations

Database migrations run automatically on deployment. To run manually:

```bash
aws ecs execute-command --cluster $CLUSTER_NAME --task $TASK_ARN --container backend --interactive --command "python -c 'from migrate_reorder_fields import migrate_database; migrate_database()'"
```

### Backup and Recovery

- **Automatic backups**: 7-day retention with point-in-time recovery
- **Manual snapshots**: Can be created before major updates
- **Cross-region backup**: Configure for disaster recovery

## 🎯 Success Criteria

After deployment, verify:

- ✅ Application accessible at load balancer URL
- ✅ Admin login works (ADMIN001 / generated password)
- ✅ Database health check passes
- ✅ All ECS tasks running
- ✅ CloudWatch logs showing no errors
- ✅ Sample data visible in application

## 📞 Support

If you encounter issues:

1. Check the deployment logs in CloudWatch
2. Run the validation script: `./scripts/validate_deployment.sh`
3. Review this troubleshooting guide
4. Check AWS service health dashboards

## 🔐 Security Notes

- Change default admin password immediately after first login
- Review and customize security groups for your environment
- Enable AWS CloudTrail for audit logging
- Consider enabling AWS Config for compliance monitoring
- Regularly update container images for security patches
