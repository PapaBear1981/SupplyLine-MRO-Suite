#!/usr/bin/env python3
"""
Generate secure keys for local testing
"""

import secrets
import base64

def generate_secure_key(length=32):
    """Generate a secure base64 encoded key"""
    return base64.b64encode(secrets.token_bytes(length)).decode('utf-8')

if __name__ == "__main__":
    print("Generating secure keys for local testing...")
    print()
    
    jwt_key = generate_secure_key(32)
    app_key = generate_secure_key(32)
    
    print(f"JWT_SECRET_KEY={jwt_key}")
    print(f"SECRET_KEY={app_key}")
    print()
    print("Copy these values to your .env file for secure local testing.")
