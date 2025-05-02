# Tool Inventory System

A comprehensive tool inventory management system built with React and Flask.

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

### Backend
- Flask
- SQLite
- Flask-SQLAlchemy
- Flask-CORS
- Flask-Session

## Getting Started

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- npm or yarn

### Installation

#### Backend Setup
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

#### Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

## Usage

- Access the application at http://localhost:5173
- Default admin credentials:
  - Employee Number: ADMIN001
  - Password: admin123

## Project Structure

```
tool-inventory-system/
├── backend/             # Flask backend
│   ├── app.py           # Main application entry point
│   ├── models.py        # Database models
│   ├── routes.py        # API routes
│   ├── config.py        # Configuration
│   ├── requirements.txt # Python dependencies
│   └── static/          # Static files
├── frontend/            # React frontend
│   ├── public/          # Public assets
│   ├── src/             # Source code
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # Redux store
│   │   ├── App.jsx      # Main App component
│   │   └── main.jsx     # Entry point
│   ├── package.json     # Node.js dependencies
│   └── vite.config.js   # Vite configuration
└── database/            # SQLite database
```

## License

MIT
