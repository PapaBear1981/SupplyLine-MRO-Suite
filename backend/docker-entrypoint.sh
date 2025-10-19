#!/bin/bash
set -e

# Ensure database and session directories exist and have correct permissions
mkdir -p /database /flask_session
chmod 755 /database /flask_session

# Execute the main command
exec "$@"

