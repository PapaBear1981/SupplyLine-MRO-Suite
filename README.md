# Tool Inventory System

A comprehensive tool inventory management system built with React and Flask.

**Current Version: 1.0.0** - See [VERSION.md](VERSION.md) for version history and release notes.

## Features

- User authentication and authorization
- Tool inventory management
- Tool checkout and return system
- User activity tracking
- Admin dashboard
- Responsive design

## Tech Stack

### Frontend
- React
- Redux Toolkit
- React Router
- React Bootstrap
- Axios
- Nginx (for production deployment)

### Backend
- Flask
- SQLite
- Flask-SQLAlchemy
- Flask-CORS
- Flask-Session
- Gunicorn (for production deployment)

### Deployment
- Docker
- Docker Compose
- Nginx (as reverse proxy)

## Getting Started

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- npm or yarn
- Docker and Docker Compose (for containerized deployment)

### Installation

#### Option 1: Local Development Setup

##### Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

##### Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

#### Option 2: Docker Deployment

The application can be easily deployed using Docker and Docker Compose:

```bash
# Clone the repository
git clone https://github.com/PapaBear1981/Basic_inventory.git
cd Basic_inventory

# Create a .env file from the example
cp .env.example .env

# Build and start the containers
docker-compose up -d

# Access the application at http://localhost
```

For more detailed instructions on Docker deployment, see [DOCKER_README.md](DOCKER_README.md).

## Usage

### Local Development
- Access the application at http://localhost:5173
- API server runs at http://localhost:5000

### Docker Deployment
- Access the application at http://localhost
- API server runs at http://localhost:5000

### Default Credentials
- Default admin credentials:
  - Employee Number: ADMIN001
  - Password: admin123

## Project Structure

```
tool-inventory-system/
├── backend/                # Flask backend
│   ├── app.py              # Main application entry point
│   ├── models.py           # Database models
│   ├── routes.py           # API routes
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Docker configuration for backend
│   ├── .dockerignore       # Files to ignore in Docker build
│   └── static/             # Static files
├── frontend/               # React frontend
│   ├── public/             # Public assets
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # Redux store
│   │   ├── App.jsx         # Main App component
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node.js dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── Dockerfile          # Docker configuration for frontend
│   ├── .dockerignore       # Files to ignore in Docker build
│   └── nginx.conf          # Nginx configuration for production
├── database/               # SQLite database
├── docker-compose.yml      # Docker Compose configuration
├── .env.example            # Example environment variables
├── DOCKER_README.md        # Docker deployment instructions
└── VERSION.md              # Version history and release notes
```

## License

MIT
