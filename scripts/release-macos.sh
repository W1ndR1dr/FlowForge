#!/bin/bash
# FlowForge macOS Release Script
# Creates signed release builds with Sparkle auto-update support

set -e

# Configuration
APP_NAME="FlowForge"
BUNDLE_ID="com.flowforge.app"
FLOWFORGE_DIR="/Users/Brian/Projects/Active/FlowForge"
APP_DIR="$FLOWFORGE_DIR/FlowForgeApp"
BUILD_DIR="$APP_DIR/build"
RELEASES_DIR="$FLOWFORGE_DIR/releases"
KEYS_DIR="$HOME/.flowforge-keys"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}FlowForge macOS Release Script${NC}"
echo "================================"

# Get version from argument or Info.plist
if [ -n "$1" ]; then
    VERSION="$1"
else
    # Read from Info.plist
    VERSION=$(defaults read "$APP_DIR/App/Info" CFBundleShortVersionString 2>/dev/null || echo "1.0.0")
fi

BUILD_NUMBER=$(defaults read "$APP_DIR/App/Info" CFBundleVersion 2>/dev/null || echo "1")

echo -e "Version: ${GREEN}$VERSION${NC} (Build $BUILD_NUMBER)"

# Create directories
mkdir -p "$RELEASES_DIR"
mkdir -p "$KEYS_DIR"

# Step 1: Generate Sparkle keys if they don't exist
PRIVATE_KEY="$KEYS_DIR/sparkle_private_key"
PUBLIC_KEY="$KEYS_DIR/sparkle_public_key"

if [ ! -f "$PRIVATE_KEY" ]; then
    echo -e "\n${BLUE}Generating Sparkle EdDSA keys...${NC}"

    # Download Sparkle if needed to get the key generation tool
    SPARKLE_VERSION="2.6.0"
    SPARKLE_DIR="$KEYS_DIR/Sparkle"

    if [ ! -d "$SPARKLE_DIR" ]; then
        echo "Downloading Sparkle..."
        curl -L "https://github.com/sparkle-project/Sparkle/releases/download/$SPARKLE_VERSION/Sparkle-$SPARKLE_VERSION.tar.xz" -o /tmp/sparkle.tar.xz
        mkdir -p "$SPARKLE_DIR"
        tar -xf /tmp/sparkle.tar.xz -C "$SPARKLE_DIR"
        rm /tmp/sparkle.tar.xz
    fi

    # Generate keys
    "$SPARKLE_DIR/bin/generate_keys" -p "$PRIVATE_KEY"

    echo -e "${GREEN}Keys generated!${NC}"
    echo "Private key: $PRIVATE_KEY"
    echo "Public key: $PUBLIC_KEY"

    # Extract and display public key
    PUBLIC_KEY_VALUE=$("$SPARKLE_DIR/bin/generate_keys" -p "$PRIVATE_KEY" --print-public-key 2>/dev/null || cat "$PUBLIC_KEY")
    echo -e "\n${BLUE}Add this public key to Info.plist (SUPublicEDKey):${NC}"
    echo "$PUBLIC_KEY_VALUE"
else
    echo -e "${GREEN}Using existing Sparkle keys${NC}"
fi

# Step 2: Regenerate Xcode project
echo -e "\n${BLUE}Regenerating Xcode project...${NC}"
cd "$APP_DIR"
xcodegen generate

# Step 3: Build Release
echo -e "\n${BLUE}Building Release...${NC}"
xcodebuild -project FlowForgeApp.xcodeproj \
    -scheme FlowForgeApp \
    -configuration Release \
    -derivedDataPath build \
    ONLY_ACTIVE_ARCH=YES \
    -quiet

# Step 4: Create release zip
echo -e "\n${BLUE}Creating release archive...${NC}"
APP_PATH="$BUILD_DIR/Build/Products/Release/$APP_NAME.app"
ZIP_NAME="$APP_NAME-$VERSION.zip"
ZIP_PATH="$RELEASES_DIR/$ZIP_NAME"

# Remove old zip if exists
rm -f "$ZIP_PATH"

# Create zip (ditto preserves code signing)
cd "$BUILD_DIR/Build/Products/Release"
ditto -c -k --keepParent "$APP_NAME.app" "$ZIP_PATH"

# Get file size
FILE_SIZE=$(stat -f%z "$ZIP_PATH")
echo "Archive created: $ZIP_PATH ($FILE_SIZE bytes)"

# Step 5: Sign the release
echo -e "\n${BLUE}Signing release with Sparkle...${NC}"
SPARKLE_DIR="$KEYS_DIR/Sparkle"
SIGNATURE=$("$SPARKLE_DIR/bin/sign_update" "$ZIP_PATH" -s "$PRIVATE_KEY")
echo "Signature: $SIGNATURE"

# Step 6: Update appcast.xml
echo -e "\n${BLUE}Updating appcast.xml...${NC}"
APPCAST="$FLOWFORGE_DIR/appcast.xml"
DOWNLOAD_URL="https://github.com/W1ndR1dr/FlowForge/releases/download/v$VERSION/$ZIP_NAME"
PUB_DATE=$(date -R)

cat > "$APPCAST" << EOF
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <channel>
        <title>FlowForge Updates</title>
        <link>https://github.com/W1ndR1dr/FlowForge</link>
        <description>FlowForge auto-update feed</description>
        <language>en</language>

        <item>
            <title>FlowForge $VERSION</title>
            <description><![CDATA[
                <h2>What's New in $VERSION</h2>
                <p>See release notes at https://github.com/W1ndR1dr/FlowForge/releases/tag/v$VERSION</p>
            ]]></description>
            <pubDate>$PUB_DATE</pubDate>
            <sparkle:version>$BUILD_NUMBER</sparkle:version>
            <sparkle:shortVersionString>$VERSION</sparkle:shortVersionString>
            <sparkle:minimumSystemVersion>14.0</sparkle:minimumSystemVersion>
            <enclosure
                url="$DOWNLOAD_URL"
                sparkle:edSignature="$SIGNATURE"
                length="$FILE_SIZE"
                type="application/octet-stream"/>
        </item>

    </channel>
</rss>
EOF

echo -e "${GREEN}Appcast updated!${NC}"

# Step 7: Copy to Applications (optional, for local testing)
echo -e "\n${BLUE}Installing to /Applications...${NC}"
rm -rf "/Applications/$APP_NAME.app"
cp -R "$APP_PATH" "/Applications/"
echo -e "${GREEN}Installed to /Applications/$APP_NAME.app${NC}"

# Summary
echo -e "\n${GREEN}Release Complete!${NC}"
echo "================================"
echo "Version: $VERSION (Build $BUILD_NUMBER)"
echo "Archive: $ZIP_PATH"
echo "Size: $FILE_SIZE bytes"
echo ""
echo "Next steps:"
echo "1. Create GitHub release: v$VERSION"
echo "2. Upload: $ZIP_PATH"
echo "3. Commit and push appcast.xml"
echo ""
echo "Run these commands:"
echo "  cd $FLOWFORGE_DIR"
echo "  git add appcast.xml"
echo "  git commit -m 'Release v$VERSION'"
echo "  git push"
echo "  gh release create v$VERSION '$ZIP_PATH' --title 'FlowForge $VERSION'"
