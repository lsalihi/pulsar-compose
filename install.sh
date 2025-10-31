#!/bin/bash

# Pulsar Compose One-Line Installer
# Automatically detects platform and installs the appropriate executable

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO="lsalihi/pulsar-compose"
GITHUB_API="https://api.github.com/repos/$REPO/releases/latest"
INSTALL_DIR="/usr/local/bin"
TEMP_DIR=$(mktemp -d)

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Cleanup function
cleanup() {
    rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

# Detect platform
detect_platform() {
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)

    case $OS in
        linux)
            case $ARCH in
                x86_64)
                    PLATFORM="linux-x64"
                    EXECUTABLE_NAME="pulsar"
                    ;;
                aarch64|arm64)
                    PLATFORM="linux-arm64"
                    EXECUTABLE_NAME="pulsar"
                    ;;
                *)
                    log_error "Unsupported Linux architecture: $ARCH"
                    exit 1
                    ;;
            esac
            ;;
        darwin)
            case $ARCH in
                x86_64)
                    PLATFORM="macos-x64"
                    EXECUTABLE_NAME="pulsar"
                    ;;
                arm64)
                    PLATFORM="macos-arm64"
                    EXECUTABLE_NAME="pulsar"
                    ;;
                *)
                    log_error "Unsupported macOS architecture: $ARCH"
                    exit 1
                    ;;
            esac
            ;;
        msys*|mingw*|cygwin*)
            PLATFORM="windows-x64"
            EXECUTABLE_NAME="pulsar.exe"
            ;;
        *)
            log_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
}

# Check if running as root (for Linux/macOS)
check_permissions() {
    if [[ "$OS" != "msys"* && "$OS" != "mingw"* && "$OS" != "cygwin"* ]]; then
        if [[ $EUID -eq 0 ]]; then
            log_warning "Running as root - this is not recommended for security reasons"
        fi

        if [[ ! -w "$INSTALL_DIR" ]]; then
            log_error "Cannot write to $INSTALL_DIR. Try running with sudo:"
            echo "sudo $0"
            exit 1
        fi
    fi
}

# Get latest release info from GitHub
get_latest_release() {
    log_info "Fetching latest release information..."

    if command -v curl >/dev/null 2>&1; then
        RELEASE_DATA=$(curl -s "$GITHUB_API")
    elif command -v wget >/dev/null 2>&1; then
        RELEASE_DATA=$(wget -q -O - "$GITHUB_API")
    else
        log_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi

    if [[ -z "$RELEASE_DATA" ]]; then
        log_error "Failed to fetch release information from GitHub"
        exit 1
    fi

    # Extract download URL for our platform
    DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep -o "https://github.com/$REPO/releases/download/[^\"]*$EXECUTABLE_NAME" | head -1)

    if [[ -z "$DOWNLOAD_URL" ]]; then
        log_error "Could not find executable for platform: $PLATFORM"
        log_info "Available platforms in latest release:"
        echo "$RELEASE_DATA" | grep "browser_download_url" | grep -E "(linux|macos|windows)" | sed 's/.*"https:\/\//https:\/\//' | sed 's/".*//'
        exit 1
    fi
}

# Download and install
download_and_install() {
    log_info "Downloading Pulsar Compose for $PLATFORM..."

    cd "$TEMP_DIR"

    if command -v curl >/dev/null 2>&1; then
        if ! curl -L -o "$EXECUTABLE_NAME" "$DOWNLOAD_URL"; then
            log_error "Failed to download executable"
            exit 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if ! wget -O "$EXECUTABLE_NAME" "$DOWNLOAD_URL"; then
            log_error "Failed to download executable"
            exit 1
        fi
    fi

    # Make executable (skip for Windows)
    if [[ "$OS" != "msys"* && "$OS" != "mingw"* && "$OS" != "cygwin"* ]]; then
        chmod +x "$EXECUTABLE_NAME"
    fi

    # Install to system path
    log_info "Installing to $INSTALL_DIR..."
    if ! mv "$EXECUTABLE_NAME" "$INSTALL_DIR/"; then
        log_error "Failed to install executable to $INSTALL_DIR"
        exit 1
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    if ! command -v pulsar >/dev/null 2>&1; then
        log_error "pulsar command not found in PATH"
        log_info "You may need to restart your shell or add $INSTALL_DIR to your PATH"
        exit 1
    fi

    if ! pulsar --version >/dev/null 2>&1; then
        log_error "pulsar command exists but is not working properly"
        exit 1
    fi
}

# Main installation process
main() {
    echo -e "${BLUE}🚀 Pulsar Compose One-Line Installer${NC}"
    echo

    detect_platform
    log_info "Detected platform: $PLATFORM"

    check_permissions

    get_latest_release
    log_info "Found executable: $DOWNLOAD_URL"

    download_and_install

    verify_installation

    log_success "Pulsar Compose installed successfully!"
    echo
    log_info "Run 'pulsar --help' to get started"
    log_info "Run 'pulsar --version' to verify installation"
    echo
    log_info "Need help? Visit: https://github.com/$REPO"
}

# Run main function
main "$@"