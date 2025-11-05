#!/bin/bash

# Lambda Packaging Script
# This script packages the Lambda function and its dependencies into a deployment-ready ZIP file.
# It creates a proper Python package structure that AWS Lambda can execute.

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"
PACKAGE_DIR="$DIST_DIR/package"
OUTPUT_ZIP="$DIST_DIR/lambda-package.zip"
HANDLERS_DIR="$PROJECT_ROOT/handlers"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

echo "=================================================="
echo "Lambda Function Packaging Script"
echo "=================================================="
echo ""

# Clean up previous builds
echo "→ Cleaning previous build artifacts..."
rm -rf "$DIST_DIR"
mkdir -p "$PACKAGE_DIR"
echo "  ✓ Clean complete"
echo ""

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "❌ Error: requirements.txt not found at $REQUIREMENTS_FILE"
    exit 1
fi

# Install dependencies into the package directory
echo "→ Installing Python dependencies..."
if [ -s "$REQUIREMENTS_FILE" ]; then
    # Check if there are any uncommented, non-empty lines
    if grep -v '^#' "$REQUIREMENTS_FILE" | grep -v '^[[:space:]]*$' > /dev/null; then
        pip install -r "$REQUIREMENTS_FILE" -t "$PACKAGE_DIR" --quiet
        echo "  ✓ Dependencies installed"
    else
        echo "  ⚠ No dependencies to install (requirements.txt is empty or only has comments)"
    fi
else
    echo "  ⚠ requirements.txt is empty, skipping dependency installation"
fi
echo ""

# Copy handler code to package directory
echo "→ Copying handler code..."
if [ ! -d "$HANDLERS_DIR" ]; then
    echo "❌ Error: handlers directory not found at $HANDLERS_DIR"
    exit 1
fi

# Copy the handler files directly to the root of the package
# This ensures the handler path matches what's specified in the blueprint
cp -r "$HANDLERS_DIR/resources/"* "$PACKAGE_DIR/"
echo "  ✓ Handler code copied"
echo ""

# Create the ZIP file
echo "→ Creating deployment package..."
cd "$PACKAGE_DIR"
zip -r "$OUTPUT_ZIP" . -q
cd "$PROJECT_ROOT"
echo "  ✓ Package created"
echo ""

# Get package size
PACKAGE_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)

# Display summary
echo "=================================================="
echo "Packaging Complete!"
echo "=================================================="
echo ""
echo "📦 Package Location: $OUTPUT_ZIP"
echo "📊 Package Size: $PACKAGE_SIZE"
echo ""
echo "Next Steps:"
echo "  Deploy using Bluelink CLI: bluelink deploy"
echo ""

# Verify the package contents
echo "Package Contents:"
echo "--------------------------------------------------"
unzip -l "$OUTPUT_ZIP" | head -20
echo "..."
echo ""

exit 0
