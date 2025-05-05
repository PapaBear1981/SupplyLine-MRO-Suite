#!/bin/sh

# Update version in MainLayout.jsx
sed -i 's/Version [0-9]\+\.[0-9]\+\.[0-9]\+/Version 1.1.1/g' src/components/common/MainLayout.jsx

echo "Updated version to 1.1.1 in MainLayout.jsx"
