#!/bin/sh

# This script updates the version number across the application
# Usage: ./update_version.sh <new_version>

if [ -z "$1" ]; then
  echo "Error: Version number is required"
  echo "Usage: ./update_version.sh <new_version>"
  exit 1
fi

NEW_VERSION=$1

# Update version in version.js
sed -i "s/APP_VERSION = '[0-9]\+\.[0-9]\+\.[0-9]\+'/APP_VERSION = '$NEW_VERSION'/g" src/utils/version.js

# Update version in package.json
sed -i "s/\"version\": \"[0-9]\+\.[0-9]\+\.[0-9]\+\"/\"version\": \"$NEW_VERSION\"/g" package.json

echo "Updated version to $NEW_VERSION in the application"
