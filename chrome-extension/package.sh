#!/bin/bash
# Package Chrome Extension for distribution

echo "Packaging Synapse Chrome Extension..."

# Create dist directory
mkdir -p dist

# Copy all necessary files
cp manifest.json dist/
cp background.js dist/
cp content.js dist/
cp icon16.png dist/ 2>/dev/null || echo "icon16.png not found, skipping"
cp icon48.png dist/ 2>/dev/null || echo "icon48.png not found, skipping"
cp icon128.png dist/ 2>/dev/null || echo "icon128.png not found, skipping"

# Create ZIP package
cd dist
zip -r ../synapse-extension.zip .
cd ..

echo "✓ Extension packaged to: synapse-extension.zip"
echo ""
echo "To install in Chrome:"
echo "1. Open chrome://extensions/"
echo "2. Enable 'Developer mode'"
echo "3. Extract synapse-extension.zip to a folder"
echo "4. Click 'Load unpacked' and select the extracted folder"
echo ""
echo "Or upload synapse-extension.zip to Chrome Web Store for publishing"
