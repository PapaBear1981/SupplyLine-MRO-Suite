#!/bin/sh

# Update version in MainLayout.jsx
sed -i 's/Version [0-9]\+\.[0-9]\+\.[0-9]\+/Version 2.0.0/g' src/components/common/MainLayout.jsx

echo "Updated version to 2.0.0 in MainLayout.jsx"
