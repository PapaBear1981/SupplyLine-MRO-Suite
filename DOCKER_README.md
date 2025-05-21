# Docker Deployment Guide for SupplyLine MRO Suite

This guide explains how to deploy the SupplyLine MRO Suite using Docker and Docker Compose.

## Prerequisites

- Docker Engine (version 24.0.0 or higher)
- Docker Compose (version 2.20.0 or higher)
- Git (to clone the repository)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/PapaBear1981/SupplyLine-MRO-Suite.git
cd SupplyLine-MRO-Suite
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory by copying the example file:

```bash
cp .env.example .env
```

Edit the `.env` file to set your environment variables:

```
# Backend Environment Variables
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
CORS_ORIGINS=http://localhost,http://localhost:80
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1

# Frontend Environment Variables
VITE_API_URL=http://localhost:5000

# Docker Compose Resource Limits (optional)
BACKEND_CPU_LIMIT=0.5
BACKEND_MEMORY_LIMIT=512M
FRONTEND_CPU_LIMIT=0.3
FRONTEND_MEMORY_LIMIT=256M
```

### 3. Build and Start the Containers

```bash
docker-compose up -d --build
```

This command will:
- Build the Docker images for the frontend and backend
- Start the containers in detached mode
- Create the necessary volumes for persistent data

### 4. Initialize the Database (First Run Only)

For the first run, you need to initialize the database:

```bash
docker-compose exec backend python init_db.py
```

### 5. Access the Application

- Frontend: http://localhost
- Backend API: http://localhost:5000

Default admin credentials:
- Employee Number: ADMIN001
- Password: admin123

## Container Management

### View Container Logs

```bash
# View logs for all containers
docker-compose logs

# View logs for a specific container
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Check Container Health Status

```bash
# Check health status of all containers
docker-compose ps

# Get detailed health status
docker inspect --format "{{.Name}} - {{.State.Health.Status}}" $(docker-compose ps -q)
```

### Stop the Containers

```bash
docker-compose down
```

### Restart the Containers

```bash
docker-compose restart
```

### Rebuild and Restart (After Code Changes)

```bash
docker-compose up -d --build
```

### Updating to a New Version

When updating to a new version of the application:

1. Pull the latest changes from the repository:
   ```bash
   git pull origin master
   ```

2. Rebuild the containers to apply the changes:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

The update process includes:
- Automatic database schema updates
- Updated frontend with the latest features
- Version number updates in the UI

## Data Persistence

The application uses Docker volumes to persist data:

- `database`: Stores the SQLite database file
- `flask_session`: Stores Flask session data

These volumes ensure your data is preserved even when containers are restarted or rebuilt.

## Troubleshooting

### Database Connection Issues

If the backend cannot connect to the database:

1. Check if the database volume is properly mounted:
   ```bash
   docker-compose exec backend ls -la /database
   ```

2. Verify the database file exists:
   ```bash
   docker-compose exec backend ls -la /database/tools.db
   ```

3. Check database permissions:
   ```bash
   docker-compose exec backend ls -la /database/tools.db
   ```

### CORS Issues

If you encounter CORS errors:

1. Check the CORS settings in the `.env` file
2. Make sure the frontend is accessing the backend using the correct URL
3. Verify the CORS headers in the backend response:
   ```bash
   curl -I -X OPTIONS http://localhost:5000/api/health
   ```

### Container Health Checks

Check the health status of your containers:

```bash
docker-compose ps
```

### Permission Issues

If you encounter permission issues:

1. Check the ownership of the mounted volumes:
   ```bash
   docker-compose exec backend ls -la /database
   docker-compose exec backend ls -la /flask_session
   ```

2. Verify that the application has write access to the necessary directories:
   ```bash
   docker-compose exec backend touch /database/test.txt
   docker-compose exec backend rm /database/test.txt
   ```

## Production Deployment Considerations

For production deployment, consider the following additional steps:

1. Use a proper reverse proxy (like Nginx or Traefik) in front of your containers
2. Set up HTTPS with SSL certificates
3. Use a more robust database solution (PostgreSQL, MySQL)
4. Implement proper logging and monitoring
5. Set up automatic backups for your data
6. Use Docker Swarm or Kubernetes for container orchestration in larger deployments
7. Implement container resource limits based on your server capacity
8. Set up a CI/CD pipeline for automated testing and deployment
9. Use Docker content trust for image verification
10. Implement proper secrets management (Docker secrets or Kubernetes secrets)

## Security Considerations

1. Never use the default admin credentials in production
2. Regularly update all dependencies and base images
3. Scan container images for vulnerabilities using tools like Trivy or Snyk
4. Implement proper network segmentation
5. Use read-only file systems where possible
6. Limit container capabilities and resources
7. Monitor container logs for suspicious activities
