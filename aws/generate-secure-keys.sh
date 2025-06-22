#!/bin/bash

# Generate Secure Keys for SupplyLine MRO Suite
# This script generates cryptographically secure keys for Issue #364

echo "🔐 Generating Secure Keys for SupplyLine MRO Suite"
echo "=================================================="
echo

# Generate JWT Secret Key (64 characters, base64 encoded)
echo "🔑 Generating JWT Secret Key..."
JWT_SECRET=$(openssl rand -base64 48 | tr -d '\n')
echo "JWT_SECRET_KEY: $JWT_SECRET"
echo

# Generate App Secret Key (64 characters, base64 encoded)
echo "🔑 Generating App Secret Key..."
APP_SECRET=$(openssl rand -base64 48 | tr -d '\n')
echo "APP_SECRET_KEY: $APP_SECRET"
echo

# Generate Database Password (32 characters, alphanumeric + symbols)
echo "🔑 Generating Database Password..."
DB_PASSWORD=$(openssl rand -base64 32 | tr -d '\n' | head -c 32)
echo "DATABASE_PASSWORD: $DB_PASSWORD"
echo

echo "=================================================="
echo "🚀 CloudFormation Deployment Command:"
echo "=================================================="
echo
echo "aws cloudformation update-stack \\"
echo "  --stack-name supplyline-application \\"
echo "  --template-body file://aws/cloudformation/application-simple.yaml \\"
echo "  --parameters \\"
echo "    ParameterKey=JWTSecretKey,ParameterValue=\"$JWT_SECRET\" \\"
echo "    ParameterKey=AppSecretKey,ParameterValue=\"$APP_SECRET\" \\"
echo "    ParameterKey=DatabasePassword,ParameterValue=\"$DB_PASSWORD\""
echo

echo "=================================================="
echo "⚠️  SECURITY NOTES:"
echo "=================================================="
echo "1. Save these keys in a secure password manager"
echo "2. Do NOT commit these keys to version control"
echo "3. Use different keys for each environment"
echo "4. Rotate keys regularly"
echo "5. All existing JWT tokens will be invalidated"
echo

echo "✅ Secure keys generated successfully!"
