#!/bin/bash
# FlowForge iOS TestFlight Release Script
# Builds, archives, and uploads to TestFlight

set -e

# Configuration
APP_NAME="FlowForge"
SCHEME="FlowForgeApp-iOS"
FLOWFORGE_DIR="/Users/Brian/Projects/Active/FlowForge"
APP_DIR="$FLOWFORGE_DIR/FlowForgeApp"
BUILD_DIR="$APP_DIR/build"

# App Store Connect API credentials
API_KEY_PATH="/Users/Brian/.private_keys/AuthKey_T8Y37Z8R8T.p8"
API_KEY_ID="T8Y37Z8R8T"
API_ISSUER_ID="e2dd9f59-df19-469f-b27e-72b1ecaadeda"
TEAM_ID="2H43Q8Y3CR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}FlowForge iOS TestFlight Release Script${NC}"
echo "========================================"

cd "$APP_DIR"

# Get version from Info.plist
VERSION=$(defaults read "$APP_DIR/App-iOS/Info" CFBundleShortVersionString 2>/dev/null || echo "1.0.0")
BUILD_NUMBER=$(defaults read "$APP_DIR/App-iOS/Info" CFBundleVersion 2>/dev/null || echo "1")

echo -e "Version: ${GREEN}$VERSION${NC} (Build $BUILD_NUMBER)"

# Step 1: Regenerate Xcode project
echo -e "\n${BLUE}Regenerating Xcode project...${NC}"
xcodegen generate

# Step 2: Archive
echo -e "\n${BLUE}Archiving iOS app...${NC}"
rm -rf "$BUILD_DIR/$SCHEME.xcarchive"
xcodebuild -project FlowForgeApp.xcodeproj \
  -scheme "$SCHEME" \
  -configuration Release \
  -destination "generic/platform=iOS" \
  -archivePath "$BUILD_DIR/$SCHEME.xcarchive" \
  archive \
  CODE_SIGN_STYLE=Automatic \
  DEVELOPMENT_TEAM="$TEAM_ID" \
  -quiet

echo -e "${GREEN}Archive created!${NC}"

# Step 3: Export and Upload
echo -e "\n${BLUE}Uploading to TestFlight...${NC}"
rm -rf "$BUILD_DIR/export"
xcodebuild -exportArchive \
  -archivePath "$BUILD_DIR/$SCHEME.xcarchive" \
  -exportPath "$BUILD_DIR/export" \
  -exportOptionsPlist ExportOptions.plist \
  -allowProvisioningUpdates \
  -authenticationKeyPath "$API_KEY_PATH" \
  -authenticationKeyID "$API_KEY_ID" \
  -authenticationKeyIssuerID "$API_ISSUER_ID"

echo -e "\n${GREEN}Upload Complete!${NC}"
echo "========================================"
echo "Version: $VERSION (Build $BUILD_NUMBER)"
echo ""
echo "Next steps:"
echo "1. Check App Store Connect for processing status"
echo "2. Once processed, the build will appear in TestFlight"
echo "3. Add testers or enable automatic distribution"
echo ""
echo "App Store Connect: https://appstoreconnect.apple.com"
