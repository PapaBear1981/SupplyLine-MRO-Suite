# Google Cloud Platform Deployment Guide

This guide explains how to deploy the SupplyLine MRO Suite to Google Cloud Platform using Cloud Run and Cloud SQL.

## Prerequisites

1. **Google Cloud Account**: Active GCP account with billing enabled
2. **Google Cloud CLI**: Install and configure `gcloud` CLI
3. **Docker**: Install Docker for local testing
4. **Project Setup**: Create a new GCP project or use an existing one

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/PapaBear1981/SupplyLine-MRO-Suite.git
cd SupplyLine-MRO-Suite
git checkout feature/google-cloud-deployment
```

### 2. Configure Environment

```bash
# Copy the environment template
cp .env.gcp.example .env.gcp

# Edit the configuration file
nano .env.gcp
```

Update the following variables in `.env.gcp`:
- `PROJECT_ID`: Your GCP project ID
- `SECRET_KEY`: Generate a secure secret key (32+ characters)
- `DB_PASSWORD`: Secure database password
- Other variables as needed

### 3. Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 4. Deploy

```bash
# Make the deployment script executable
chmod +x deploy-gcp.sh

# Run the deployment
./deploy-gcp.sh
```

The script automatically creates the service accounts `supplyline-backend-sa` and
`supplyline-frontend-sa` with the required IAM roles and sets up a VPC Access
connector if they do not already exist.

## Manual Deployment Steps

If you prefer to deploy manually or need more control:

### 1. Enable APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Create Secrets

```bash
# Create application secret key
echo -n "your-secret-key" | gcloud secrets create supplyline-secret-key --data-file=-

# Create database credentials
echo -n "supplyline_user" | gcloud secrets create supplyline-db-username --data-file=-
echo -n "your-db-password" | gcloud secrets create supplyline-db-password --data-file=-
```

### 3. Create Service Accounts

```bash
gcloud iam service-accounts create supplyline-backend-sa --display-name="SupplyLine Backend"
gcloud iam service-accounts create supplyline-frontend-sa --display-name="SupplyLine Frontend"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:supplyline-backend-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.serviceAgent"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:supplyline-backend-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:supplyline-frontend-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.serviceAgent"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:supplyline-frontend-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"
```

### 4. Configure VPC Access Connector

```bash
gcloud compute networks vpc-access connectors create supplyline-connector \
    --region=REGION \
    --network=default \
    --range=10.8.0.0/28
```

### 5. Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create supplyline-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB

# Create database
gcloud sql databases create supplyline --instance=supplyline-db

# Create user
gcloud sql users create supplyline_user \
    --instance=supplyline-db \
    --password=your-secure-password
```

### 6. Build and Deploy

```bash
# Submit build to Cloud Build
gcloud builds submit --config=cloudbuild.yaml
```

### 7. Initialize Database

Database initialization is now handled automatically by `deploy-gcp.sh`. After the
Cloud SQL instance is created, the script invokes `backend/cloud_sql_init.py`
through the Cloud SQL Auth proxy to create all tables and the default admin user.

If you ever need to run the initialization manually, start the Cloud SQL Proxy and
execute the script:

```bash
./cloud_sql_proxy -instances=PROJECT_ID:REGION:supplyline-db=tcp:5432 &
python backend/cloud_sql_init.py
```

## Configuration

### Environment Variables

The application uses the following environment variables:

#### Backend (Cloud Run)
- `FLASK_ENV`: Set to `production`
- `SECRET_KEY`: Application secret key
- `DB_HOST`: Cloud SQL connection string
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name
- `CORS_ORIGINS`: Allowed frontend origins

#### Frontend (Build-time)
- `VITE_API_URL`: Backend API URL

### Resource Limits

Default resource limits for Cloud Run services:

#### Backend
- CPU: 1 vCPU
- Memory: 1 GiB
- Max instances: 10

#### Frontend
- CPU: 0.5 vCPU
- Memory: 512 MiB
- Max instances: 5

## Security

### Authentication
- Admin credentials: `ADMIN001` / `admin123` (change after first login)
- User sessions stored in database
- HTTPS enforced in production

### Database Security
- Cloud SQL with private IP
- Encrypted connections
- Regular automated backups

### Application Security
- CORS configured for specific origins
- Security headers enabled
- Session management with secure cookies

## Monitoring

### Cloud Logging
Application logs are automatically sent to Cloud Logging.

### Health Checks
Both services include health check endpoints:
- Backend: `/api/health`
- Frontend: `/`

### Metrics
Monitor your deployment using Cloud Monitoring:
- Request latency
- Error rates
- Resource utilization

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Cloud Build logs
   - Verify Dockerfile syntax
   - Ensure all dependencies are listed

2. **Database Connection Issues**
   - Verify Cloud SQL instance is running
   - Check connection string format
   - Ensure database user has proper permissions

3. **CORS Errors**
   - Update `CORS_ORIGINS` environment variable
   - Ensure frontend URL matches exactly

### Logs

View application logs:
```bash
# Backend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=supplyline-backend-staging"

# Frontend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=supplyline-frontend-staging"
```

## Scaling

### Automatic Scaling
Cloud Run automatically scales based on traffic:
- Scales to zero when no traffic
- Scales up based on CPU and memory usage
- Configurable max instances

### Manual Scaling
Update service configuration:
```bash
gcloud run services update supplyline-backend-staging \
    --max-instances=20 \
    --region=us-central1
```

## Backup and Recovery

### Database Backups
Cloud SQL automatically creates daily backups:
- Point-in-time recovery available
- Configurable backup retention
- Cross-region backup replication

### Application State
- User sessions stored in database
- File uploads stored in Cloud Storage (if configured)

## Cost Optimization

### Tips to Reduce Costs
1. Use appropriate instance sizes
2. Configure auto-scaling properly
3. Monitor and optimize database usage
4. Use Cloud Storage for static assets
5. Implement caching strategies

## Support

For deployment issues:
1. Check the troubleshooting section
2. Review Cloud Build and Cloud Run logs
3. Verify environment configuration
4. Test database connectivity

## Next Steps

After successful deployment:
1. Change default admin password
2. Configure custom domain (optional)
3. Set up monitoring alerts
4. Configure backup policies
5. Implement CI/CD pipeline
