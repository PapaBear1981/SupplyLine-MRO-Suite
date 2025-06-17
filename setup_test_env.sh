#!/bin/bash

# Setup Testing Environment for SupplyLine MRO Suite
# This script sets up the required environment variables and prepares the testing environment

echo "🔧 Setting up SupplyLine MRO Suite Testing Environment"
echo "=" * 50

# Check if .env file exists
if [ -f ".env" ]; then
    echo "📄 Found existing .env file"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [[ $overwrite != "y" && $overwrite != "Y" ]]; then
        echo "ℹ️  Using existing .env file"
        source .env
        exit 0
    fi
fi

# Create .env file with testing credentials
echo "📝 Creating .env file with testing credentials..."

cat > .env << 'EOF'
# SupplyLine MRO Suite Testing Environment Variables

# Admin user credentials for testing
export SL_ADMIN_EMP_NUM="ADMIN001"
export SL_ADMIN_PWD="admin123"

# Admin password for reset script
export ADMIN_INIT_PASSWORD="admin123"

# Application secret key (development only - use secure key in production)
export SECRET_KEY="dev-testing-key-not-for-production"

# API Base URL
export API_BASE_URL="http://localhost:5000"

# Database path
export DB_PATH="database/tools.db"
EOF

echo "✅ Created .env file with testing credentials"

# Make the script executable
chmod +x setup_test_env.sh

# Source the environment variables
echo "🔄 Loading environment variables..."
source .env

echo "✅ Environment variables loaded"

# Verify environment variables are set
echo "🔍 Verifying environment variables..."

if [ -z "$SL_ADMIN_EMP_NUM" ]; then
    echo "❌ SL_ADMIN_EMP_NUM not set"
    exit 1
else
    echo "✅ SL_ADMIN_EMP_NUM: $SL_ADMIN_EMP_NUM"
fi

if [ -z "$SL_ADMIN_PWD" ]; then
    echo "❌ SL_ADMIN_PWD not set"
    exit 1
else
    echo "✅ SL_ADMIN_PWD: [HIDDEN]"
fi

if [ -z "$ADMIN_INIT_PASSWORD" ]; then
    echo "❌ ADMIN_INIT_PASSWORD not set"
    exit 1
else
    echo "✅ ADMIN_INIT_PASSWORD: [HIDDEN]"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY not set"
    exit 1
else
    echo "✅ SECRET_KEY: [HIDDEN]"
fi

echo ""
echo "🎉 Testing environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the backend server: cd backend && python app.py"
echo "2. Start the frontend server: cd frontend && npm run dev"
echo "3. Run tests: python security_tests.py"
echo ""
echo "💡 To load these variables in a new shell session, run:"
echo "   source .env"
echo ""
echo "⚠️  SECURITY NOTE: This .env file contains development credentials."
echo "   Do not use these credentials in production!"
