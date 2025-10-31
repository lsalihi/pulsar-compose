#!/bin/bash

# Pulsar Compose Executable Installer
# This script downloads and installs the Pulsar Compose executable

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Pulsar Compose Executable Installer${NC}"
echo "=================================="

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case $OS in
    linux)
        if [[ "$ARCH" == "x86_64" ]]; then
            PACKAGE="pulsar-compose-linux-x64.tar.gz"
        else
            echo -e "${RED}Unsupported architecture: $ARCH${NC}"
            exit 1
        fi
        ;;
    darwin)
        if [[ "$ARCH" == "x86_64" ]]; then
            PACKAGE="pulsar-compose-macos-x64.tar.gz"
        elif [[ "$ARCH" == "arm64" ]]; then
            PACKAGE="pulsar-compose-macos-arm64.tar.gz"
        else
            echo -e "${RED}Unsupported architecture: $ARCH${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo -e "${YELLOW}Downloading Pulsar Compose executable...${NC}"

# TODO: Replace with actual download URL when releases are published
# For now, this is a placeholder
DOWNLOAD_URL="https://github.com/lsalihi/pulsar-compose/releases/latest/download/$PACKAGE"

if command -v curl >/dev/null 2>&1; then
    curl -L -o "$PACKAGE" "$DOWNLOAD_URL"
elif command -v wget >/dev/null 2>&1; then
    wget -O "$PACKAGE" "$DOWNLOAD_URL"
else
    echo -e "${RED}Neither curl nor wget found. Please install one of them.${NC}"
    exit 1
fi

echo -e "${YELLOW}Extracting...${NC}"
tar -xzf "$PACKAGE"

echo -e "${YELLOW}Installing to /usr/local/bin...${NC}"

# Check if we have sudo
if [[ $EUID -eq 0 ]]; then
    cp -r pulsar /usr/local/bin/
    chmod +x /usr/local/bin/pulsar
else
    sudo cp -r pulsar /usr/local/bin/
    sudo chmod +x /usr/local/bin/pulsar
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "You can now use Pulsar Compose:"
echo "  pulsar --help"
echo "  pulsar version"
echo ""
echo "For more information, visit: https://github.com/lsalihi/pulsar-compose"