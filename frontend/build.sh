#!/bin/bash
# Build script for Malka Money Frontend
# This script builds the React app using Vite

echo "Building Malka Money Frontend..."

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Run the build
npm run build

echo "Build complete. Output in dist/ directory."