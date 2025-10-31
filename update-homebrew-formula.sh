#!/bin/bash

# Script to update Homebrew formula with SHA256 hashes from GitHub release
# Usage: ./update-homebrew-formula.sh v0.1.0

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 v0.1.0"
    exit 1
fi

VERSION=$1
FORMULA_FILE="pulsar.rb"

echo "Updating Homebrew formula for version $VERSION..."

# Get SHA256 hashes from GitHub API
get_sha256() {
    local platform=$1
    local asset_name="pulsar-compose-${platform}.tar.gz"

    echo "Getting SHA256 for $asset_name..." >&2

    # Use GitHub API to get release asset info
    curl -s "https://api.github.com/repos/lsalihi/pulsar-compose/releases/tags/$VERSION" |
    jq -r ".assets[] | select(.name == \"$asset_name\") | .browser_download_url" |
    xargs curl -sL | sha256sum | cut -d' ' -f1
}

# Update Linux SHA256
LINUX_SHA=$(get_sha256 "linux-x64")
if [ -n "$LINUX_SHA" ] && [ "$LINUX_SHA" != "null" ]; then
    echo "Linux SHA256: $LINUX_SHA"
    sed -i "s|sha256 \"YOUR_SHA256_HERE\"  # Replace with actual SHA256 for Linux|sha256 \"$LINUX_SHA\"|g" "$FORMULA_FILE"
else
    echo "Warning: Could not get Linux SHA256"
fi

# Update macOS x64 SHA256
MACOS_X64_SHA=$(get_sha256 "macos-x64")
if [ -n "$MACOS_X64_SHA" ] && [ "$MACOS_X64_SHA" != "null" ]; then
    echo "macOS x64 SHA256: $MACOS_X64_SHA"
    sed -i "s|sha256 \"YOUR_SHA256_HERE\"  # Replace with actual SHA256 for x64|sha256 \"$MACOS_X64_SHA\"|g" "$FORMULA_FILE"
else
    echo "Warning: Could not get macOS x64 SHA256"
fi

# Update macOS ARM64 SHA256
MACOS_ARM64_SHA=$(get_sha256 "macos-arm64")
if [ -n "$MACOS_ARM64_SHA" ] && [ "$MACOS_ARM64_SHA" != "null" ]; then
    echo "macOS ARM64 SHA256: $MACOS_ARM64_SHA"
    sed -i "s|sha256 \"YOUR_SHA256_HERE\"  # Replace with actual SHA256 for ARM64|sha256 \"$MACOS_ARM64_SHA\"|g" "$FORMULA_FILE"
else
    echo "Warning: Could not get macOS ARM64 SHA256"
fi

# Update version in URLs
sed -i "s|v0.1.0|$VERSION|g" "$FORMULA_FILE"

echo "Formula updated successfully!"
echo "Please commit and push the changes to update the Homebrew tap."