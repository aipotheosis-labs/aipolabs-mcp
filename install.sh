#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[ACI MCP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ACI MCP Error]${NC} $1"
    exit 1
}

print_warning() {
    echo -e "${YELLOW}[ACI MCP Warning]${NC} $1"
}

# Check if Python 3.10+ is installed
check_python() {
    if ! command -v python3 &>/dev/null; then
        print_error "Python 3 is not installed"
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if ! command -v bc &>/dev/null; then
        print_error "bc command not found. Please install bc to check Python version"
    fi

    # Convert version to comparable number (e.g., 3.9 -> 309, 3.10 -> 310)
    VERSION_NUM=$(echo "$PYTHON_VERSION" | tr -d '.')
    if [ "$VERSION_NUM" -lt 310 ]; then
        print_error "Python 3.10 or higher is required. Found Python $PYTHON_VERSION"
    fi

    print_message "Found Python $PYTHON_VERSION"
}

# Install uv if not present
install_uv() {
    if ! command -v uv &>/dev/null; then
        print_message "Installing uv package manager..."
        if ! curl -sSf https://install.pypa.io/get-pip.py | python3 -; then
            print_error "Failed to install pip"
        fi
        if ! python3 -m pip install uv; then
            print_error "Failed to install uv"
        fi
    else
        print_message "uv is already installed"
    fi
}

# Install aci-mcp
install_aci_mcp() {
    print_message "Installing aci-mcp..."
    if ! uvx aci-mcp --help &>/dev/null; then
        if ! pip install aci-mcp; then
            print_error "Failed to install aci-mcp"
        fi
    fi
}

# Create configuration directory and files
setup_config() {
    CONFIG_DIR="$HOME/.aci-mcp"
    if ! mkdir -p "$CONFIG_DIR"; then
        print_error "Failed to create config directory at $CONFIG_DIR"
    fi
    
    # Create config file if it doesn't exist
    if [ ! -f "$CONFIG_DIR/config" ]; then
        if ! cat > "$CONFIG_DIR/config" << EOL
# ACI MCP Configuration
# Add your ACI API key and other configurations here
ACI_API_KEY=""
LINKED_ACCOUNT_OWNER_ID=""
SERVER_TYPE="unified"  # or "apps"
APPS=""  # Comma-separated list of apps for apps-server
EOL
        then
            print_error "Failed to create config file at $CONFIG_DIR/config"
        fi
        print_message "Created configuration file at $CONFIG_DIR/config"
        chmod 600 "$CONFIG_DIR/config"
    fi
}

# Create environment-specific setup scripts
create_env_scripts() {
    CONFIG_DIR="$HOME/.aci-mcp"
    
    # Create Cursor setup script
    if ! cat > "$CONFIG_DIR/setup-cursor.sh" << 'EOL'
#!/bin/bash
# Setup script for Cursor IDE
export ACI_MCP_CONFIG="$HOME/.aci-mcp/config"
source "$ACI_MCP_CONFIG"
uvx aci-mcp $SERVER_TYPE --linked-account-owner-id "$LINKED_ACCOUNT_OWNER_ID" ${APPS:+--apps "$APPS"}
EOL
    then
        print_error "Failed to create Cursor setup script"
    fi
    chmod +x "$CONFIG_DIR/setup-cursor.sh"
    
    # Create Claude desktop setup script
    if ! cat > "$CONFIG_DIR/setup-claude.sh" << 'EOL'
#!/bin/bash
# Setup script for Claude desktop
export ACI_MCP_CONFIG="$HOME/.aci-mcp/config"
source "$ACI_MCP_CONFIG"
uvx aci-mcp $SERVER_TYPE --linked-account-owner-id "$LINKED_ACCOUNT_OWNER_ID" ${APPS:+--apps "$APPS"}
EOL
    then
        print_error "Failed to create Claude desktop setup script"
    fi
    chmod +x "$CONFIG_DIR/setup-claude.sh"
}

# Main installation process
main() {
    print_message "Starting ACI MCP installation..."
    
    # Check Python version
    check_python
    
    # Install uv
    install_uv
    
    # Install aci-mcp
    install_aci_mcp
    
    # Setup configuration
    setup_config
    
    # Create environment scripts
    create_env_scripts
    
    print_message "Installation complete!"
    print_message "Next steps:"
    print_message "1. Edit $HOME/.aci-mcp/config to add your ACI API key and other settings"
    print_message "2. Run the appropriate setup script for your environment:"
    print_message "   - For Cursor: $HOME/.aci-mcp/setup-cursor.sh"
    print_message "   - For Claude desktop: $HOME/.aci-mcp/setup-claude.sh"
}

# Run main installation
main 