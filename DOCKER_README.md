# Docker Deployment Guide for Tool Inventory System

This guide explains how to deploy the Tool Inventory System using Docker and Docker Compose.

## Prerequisites

- Docker Engine (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Git (to clone the repository)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/PapaBear1981/Basic_inventory.git
cd Basic_inventory
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

# Frontend Environment Variables
VITE_API_URL=http://localhost:5000
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
   docker-compose exec backend ls -la /app/database
   ```

2. Verify the database file exists:
   ```bash
   docker-compose exec backend ls -la /app/database/tools.db
   ```

### CORS Issues

If you encounter CORS errors:

1. Check the CORS settings in the `.env` file
2. Make sure the frontend is accessing the backend using the correct URL

### Container Health Checks

Check the health status of your containers:

```bash
docker-compose ps
```

## Production Deployment Considerations

For production deployment, consider the following additional steps:

1. Use a proper reverse proxy (like Nginx or Traefik) in front of your containers
2. Set up HTTPS with SSL certificates
3. Use a more robust database solution (PostgreSQL, MySQL)
4. Implement proper logging and monitoring
5. Set up automatic backups for your data
6. Use Docker Swarm or Kubernetes for container orchestration in larger deployments
