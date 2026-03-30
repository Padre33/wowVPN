#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR/build"
APP_BUNDLE="$BUILD_DIR/Aivpn.app"
CONTENTS="$APP_BUNDLE/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"

echo "🔨 Building AIVPN macOS app (Universal Binary)..."

# Clean
rm -rf "$BUILD_DIR"
mkdir -p "$MACOS" "$RESOURCES" "$BUILD_DIR/arm64" "$BUILD_DIR/x86_64"

# Compile for arm64
echo "📦 Compiling for arm64 (Apple Silicon)..."
swiftc \
    -o "$BUILD_DIR/arm64/Aivpn" \
    -target arm64-apple-macosx13.0 \
    -parse-as-library \
    -framework Cocoa \
    -framework SwiftUI \
    -framework Security \
    -framework Foundation \
    -module-name Aivpn \
    "$SCRIPT_DIR/AivpnApp.swift" \
    "$SCRIPT_DIR/ContentView.swift" \
    "$SCRIPT_DIR/VPNManager.swift" \
    "$SCRIPT_DIR/LocalizationManager.swift" \
    "$SCRIPT_DIR/KeychainHelper.swift"

# Compile for x86_64
echo "📦 Compiling for x86_64 (Intel)..."
swiftc \
    -o "$BUILD_DIR/x86_64/Aivpn" \
    -target x86_64-apple-macosx13.0 \
    -parse-as-library \
    -framework Cocoa \
    -framework SwiftUI \
    -framework Security \
    -framework Foundation \
    -module-name Aivpn \
    "$SCRIPT_DIR/AivpnApp.swift" \
    "$SCRIPT_DIR/ContentView.swift" \
    "$SCRIPT_DIR/VPNManager.swift" \
    "$SCRIPT_DIR/LocalizationManager.swift" \
    "$SCRIPT_DIR/KeychainHelper.swift"

# Create universal binary with lipo
echo "🔗 Creating universal binary..."
lipo -create \
    "$BUILD_DIR/arm64/Aivpn" \
    "$BUILD_DIR/x86_64/Aivpn" \
    -output "$MACOS/Aivpn"

echo "  ✅ $(file "$MACOS/Aivpn" | sed 's/.*: //')"

# Copy aivpn-client binary into Resources
echo "📦 Bundling aivpn-client binary..."
# Check for universal binary first, then fall back to native builds
CLIENT_BIN_UNIVERSAL="$PROJECT_DIR/releases/aivpn-client-universal"
CLIENT_BIN_X86="$PROJECT_DIR/target/release/aivpn-client"
CLIENT_BIN_ARM="$PROJECT_DIR/target/aarch64-apple-darwin/release/aivpn-client"

if [ -f "$CLIENT_BIN_UNIVERSAL" ]; then
    # Use pre-built universal binary
    cp "$CLIENT_BIN_UNIVERSAL" "$RESOURCES/aivpn-client"
    chmod +x "$RESOURCES/aivpn-client"
    echo "  ✅ aivpn-client bundled (Universal Binary: $(file "$RESOURCES/aivpn-client" | sed 's/.*: //'))"
elif [ -f "$CLIENT_BIN_X86" ] && [ -f "$CLIENT_BIN_ARM" ]; then
    # Create universal binary on the fly
    echo "  🔄 Creating Universal Binary from x86_64 + arm64..."
    lipo -create "$CLIENT_BIN_X86" "$CLIENT_BIN_ARM" -output "$RESOURCES/aivpn-client"
    chmod +x "$RESOURCES/aivpn-client"
    echo "  ✅ aivpn-client bundled (Universal Binary: $(file "$RESOURCES/aivpn-client" | sed 's/.*: //'))"
elif [ -f "$CLIENT_BIN_X86" ]; then
    # Fallback to x86_64 only
    cp "$CLIENT_BIN_X86" "$RESOURCES/aivpn-client"
    chmod +x "$RESOURCES/aivpn-client"
    echo "  ⚠️  aivpn-client bundled (x86_64 only)"
else
    echo "  ⚠️  aivpn-client not found"
    echo "  Run 'cargo build --release --bin aivpn-client' first"
fi

# Copy helper script into Resources
echo "📦 Bundling helper script..."
cp "$SCRIPT_DIR/aivpn_helper.sh" "$RESOURCES/aivpn_helper.sh"
chmod +x "$RESOURCES/aivpn_helper.sh"
echo "  ✅ aivpn_helper.sh bundled"

# Copy Info.plist
cp "$SCRIPT_DIR/Info.plist" "$CONTENTS/Info.plist"

# Copy app icon
if [ -f "/tmp/Aivpn.icns" ]; then
    cp /tmp/Aivpn.icns "$RESOURCES/AppIcon.icns"
    echo "  ✅ App icon bundled"
elif [ -f "$SCRIPT_DIR/AppIcon.icns" ]; then
    cp "$SCRIPT_DIR/AppIcon.icns" "$RESOURCES/AppIcon.icns"
    echo "  ✅ App icon bundled"
fi

# Copy entitlements
cp "$SCRIPT_DIR/Aivpn.entitlements" "$CONTENTS/Resources/"

# Create PkgInfo
echo -n "APPL????" > "$CONTENTS/PkgInfo"

# Create minimal Assets.xcassets
mkdir -p "$RESOURCES/Assets.xcassets/AppIcon.appiconset"
cat > "$RESOURCES/Assets.xcassets/AppIcon.appiconset/Contents.json" << 'EOF'
{
  "images" : [
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "16x16"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "16x16"
    },
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "32x32"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "32x32"
    },
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "128x128"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "128x128"
    },
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "256x256"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "256x256"
    },
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "512x512"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "512x512"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF

cat > "$RESOURCES/Assets.xcassets/Contents.json" << 'EOF'
{
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF

# Clean extended attributes and ad-hoc sign (required for macOS Sequoia)
echo "🔐 Signing app..."
xattr -cr "$APP_BUNDLE" 2>/dev/null
codesign --force --deep --sign - "$APP_BUNDLE" 2>/dev/null
echo "  ✅ Signed ($(du -sh "$APP_BUNDLE" | cut -f1))"

echo ""
echo "✅ Build complete: $APP_BUNDLE"
echo ""
echo "To run:"
echo "  open $APP_BUNDLE"
echo ""
echo "To create DMG:"
echo "  hdiutil create -volname AIVPN -srcfolder $APP_BUNDLE -ov -format UDZO aivpn-macos.dmg"
