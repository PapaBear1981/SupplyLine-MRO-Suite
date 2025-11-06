#!/bin/bash
set -e

# Ensure database and session directories exist
mkdir -p /database /flask_session

# Set ownership to appuser (this should work with Docker volumes)
chown -R appuser:appuser /database /flask_session 2>/dev/null || true

# Try to set permissions, but don't fail if it doesn't work (Windows volume mounts)
chmod 755 /database /flask_session 2>/dev/null || true

# Switch to appuser and execute the main command
exec gosu appuser "$@"

