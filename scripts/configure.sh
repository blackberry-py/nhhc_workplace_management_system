#!/usr/bin/env bash
set -euo pipefail


############################################################
# Constants and Variables                                  #
############################################################
SCRIPT_NAME=$(basename "$0")
LOG_FILE="/var/log/${SCRIPT_NAME%.*}.log"
TEMP_DOCKER_SCRIPT=$(mktemp)
TEMP_NODE_EXPORTER_TARBALL=$(mktemp)
TEMP_NODE_EXPORTER_DIR=$(mktemp -d)


# Initialize default values
BYPASS_DOCKER=false
BYPASS_APACHE=false
BYPASS_PROMETHEUS=false
BYPASS_PYTHON=false
DRY_RUN=false

############################################################
# Main function                                           #
############################################################
main() {
    # Initialize log file
    touch "$LOG_FILE" || error_exit "Cannot create log file at $LOG_FILE."

    check_root
    check_dependencies

    # Detect package manager
    if command -v apt-get &>/dev/null; then
        PACKAGE_MANAGER="apt-get"
    elif command -v yum &>/dev/null; then
        PACKAGE_MANAGER="yum"
    else
        error_exit "No supported package manager found (apt-get or yum)."
    fi

    setup "$@"
}
############################################################
# Usage                                                    #
############################################################
usage() {
    cat << EOF
Automatically configure a VM with Apache2, Node Exporter, and supporting tools for an application server behind a reverse proxy.

Syntax: $SCRIPT_NAME [options] doppler_project doppler_config doppler_token

Arguments:
  doppler_project     The project name in the Doppler Secret Management Platform.
  doppler_config      The configuration to use (e.g., prod, dev, staging).
  doppler_token       The Service Token from the Doppler Secrets Management Platform.

Options:
  --bypass-docker     Bypass Docker installation.
  --bypass-python     Bypass Python3 and b333asic dependency Installation.
  --bypass-apache     Bypass Apache2 installation.
  --bypass-prometheus Bypass Prometheus Node Exporter installation.
  --dry-run           Perform a trial run with no changes made.
  -h | --help         Print this help message.
EOF
}

############################################################
# Helper Functions                                         #
############################################################

# Logging functions with timestamps and levels
log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local icon="🔧"
    if [ "$level" = "WARN" ]; then
        icon="⚠️"
    elif [ "$level" = "ERROR" ]; then
        icon="‼️"
    fi
    echo "$timestamp [$icon $level] $message" | tee -a "$LOG_FILE"
    }

log_warn() {
    log "WARN" "$1"
}

log_error() {
    log "ERROR" "$1" >&2
}

log_info(){
	log "INFO" "$1"
}
# Exit with error after logging
error_exit() {
    log_error "$1"
    exit 1
}

# Cleanup function to remove temporary files
cleanup() {
    if [[ "$DRY_RUN" = false ]]; then
        rm -f "$TEMP_DOCKER_SCRIPT" "$TEMP_NODE_EXPORTER_TARBALL" "$TEMP_NODE_EXPORTER_DIR"
    fi
}
trap "echo The script is terminated; cleanup; exit" SIGINT  EXIT

# Check if the script is run as root
check_root() {
    if [[ "$EUID" -ne 0 ]]; then
        error_exit "This script must be run as root. Use sudo."
    fi
}

# Check for required commands
check_dependencies() {
    local dependencies=(sudo wget curl tar jq systemctl ufw)
    for cmd in "${dependencies[@]}"; do
        if ! command -v "$cmd" &>/dev/null; then
            error_exit "Required command '$cmd' is not installed. Please install it and retry."
        fi
    done
}

############################################################
# Installation Functions                                   #
############################################################

install_python_and_dependencies() {
    log_info "Installing Python and dependencies..."

    if [[ "$DRY_RUN" = true ]]; then
        log_info "Dry run: Skipping installation of Python and dependencies."
        return
    fi

    # Update and install base packages
    if [[ "$PACKAGE_MANAGER" == "apt-get" ]]; then
        sudo apt update -y || error_exit "apt-get update failed."
        sudo apt install -y --no-install-recommends \
            apt-transport-https \
            ca-certificates \
            apache2-utils \
            certbot \
            python3-certbot-apache \
            direnv \
            python3-pip \
            argon2 \
            curl \
            libenchant-2-dev \
            gnupg \
            make \
            git || error_exit "Failed to install Python and dependencies."
    elif [[ "$PACKAGE_MANAGER" == "yum" ]]; then
        sudo yum update -y || error_exit "yum update failed."
        sudo yum install -y \
            epel-release \
            openssl \
            ca-certificates \
            apache2-utils \
            certbot \
            python3-certbot-apache \
            direnv \
            python3-pip \
            curl \
            enchant-devel \
            gnupg \
            make \
            git || error_exit "Failed to install Python and dependencies."
    else
        error_exit "Unsupported package manager: $PACKAGE_MANAGER"
    fi

    # Add Doppler repository
    TEMP_DOPPLER_KEY="/tmp/doppler.gpg"
    TEMP_DOPPLER_LIST="/etc/apt/sources.list.d/doppler-cli.list"

    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' \
        | sudo gpg --dearmor -o "$TEMP_DOPPLER_KEY" || error_exit "Failed to download Doppler GPG key."

    if [[ "$PACKAGE_MANAGER" == "apt-get" ]]; then
        sudo mv "$TEMP_DOPPLER_KEY" /usr/share/keyrings/doppler-archive-keyring.gpg || error_exit "Failed to move Doppler GPG key."
        echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" \
            | sudo tee "$TEMP_DOPPLER_LIST" >/dev/null || error_exit "Failed to add Doppler repository."
        sudo apt update -y || error_exit "apt-get update failed after adding Doppler repository."
        sudo apt install -y --no-install-recommends doppler=3.68.0 build-essential || error_exit "Failed to install Doppler and build-essential."
    elif [[ "$PACKAGE_MANAGER" == "yum" ]]; then
        # Yum repository setup if applicable
        error_exit "Doppler repository setup for yum is not implemented."
    fi

    sudo apt-get clean || true
    sudo rm -rf /var/lib/apt/lists/* || true

    # Set Doppler token securely
    DOPPLER_ENV_FILE="/etc/profile.d/doppler.sh"
    sudo chmod 600 "$DOPPLER_ENV_FILE" || true
    echo "export DOPPLER_TOKEN=${TOKEN}" | sudo tee "$DOPPLER_ENV_FILE" >/dev/null || error_exit "Failed to set Doppler token."
    sudo chmod +x "$DOPPLER_ENV_FILE" || error_exit "Failed to set execute permission on Doppler environment file."

    log_info "Python and dependencies installed successfully."
}

install_docker() {
    log_info "Installing Docker..."

    if [[ "$DRY_RUN" = true ]]; then
        log_info "Dry run: Skipping Docker installation."
        return
    fi

    TEMP_DOCKER_SCRIPT="/tmp/get-docker.sh"
    curl -fsSL https://get.docker.com -o "$TEMP_DOCKER_SCRIPT" || error_exit "Failed to download Docker installation script."

    sudo sh "$TEMP_DOCKER_SCRIPT" &>/dev/null || error_exit "Docker installation script failed."
    rm -f "$TEMP_DOCKER_SCRIPT"

    # Add docker group if it doesn't exist
    if ! getent group docker &>/dev/null; then
        sudo groupadd docker || error_exit "Failed to create docker group."
    fi
    
    sudo usermod -aG docker "${SUDO_USER:-root}" || error_exit "Failed to add user to docker group."

    # Inform user to relog for group changes to take effect
    log_warn "Docker installed. Please log out and log back in for group changes to take effect."


    log_info "Docker installed and user added to docker group."
}

configure_apache() {
    log_info "Configuring Apache..."

    if [[ "$DRY_RUN" = true ]]; then
        log_info "Dry run: Skipping Apache configuration."
        return
    fi

    sudo a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests &>/dev/null || error_exit "Failed to enable Apache modules."

    sudo ufw allow 'Apache Full' &>/dev/null || error_exit "Failed to allow Apache Full through UFW."
    sudo ufw delete allow 'Apache' &>/dev/null || true
    sudo ufw allow 'OpenSSH' &>/dev/null || error_exit "Failed to allow OpenSSH through UFW."
    sudo ufw --force enable &>/dev/null || error_exit "Failed to enable UFW."

    # HTTP configuration
    cat <<EOF | sudo tee /etc/apache2/sites-available/000-default.conf >/dev/null
<VirtualHost *:80>
    ProxyPreserveHost On
    ServerName netthandshome.care
    ServerAlias www.netthandshome.care

    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/
</VirtualHost>
EOF

    # HTTPS configuration
    SSL_CERT_DIR="/etc/letsencrypt/live/netthandshome.care"
    if [[ -f "$SSL_CERT_DIR/fullchain.pem" ]]; then
        cat <<EOF | sudo tee /etc/apache2/sites-available/default-ssl.conf >/dev/null
<IfModule mod_ssl.c>
    <VirtualHost *:443>
        ServerName netthandshome.care
        ServerAlias www.netthandshome.care

        SSLEngine on
        SSLCertificateFile $SSL_CERT_DIR/fullchain.pem
        SSLCertificateKeyFile $SSL_CERT_DIR/privkey.pem
        SSLCertificateChainFile $SSL_CERT_DIR/chain.pem

        ProxyPreserveHost On
        ProxyPass / http://127.0.0.1:8080/
        ProxyPassReverse / http://127.0.0.1:8080/
    </VirtualHost>
</IfModule>
EOF
    else
        log_warn "Skipping HTTPS configuration: SSL certificates not found at $SSL_CERT_DIR."
    fi

    sudo a2ensite default-ssl &>/dev/null || error_exit "Failed to enable default-ssl site."
 
    # Validate Apache configuration
    if ! sudo apachectl configtest &>/dev/null; then
        error_exit "Apache configuration test failed."
    fi

    # Reload and enable Apache
    sudo systemctl reload apache2 &>/dev/null || error_exit "Failed to reload Apache."
    sudo systemctl enable apache2 &>/dev/null || error_exit "Failed to enable Apache to start on boot."
    sudo systemctl start apache2 &>/dev/null || error_exit "Failed to start Apache."

    log_info "Apache2 configured successfully."
}

install_prometheus_node_exporter() {
    log_info "Installing Prometheus Node Exporter..."

    if [[ "$DRY_RUN" = true ]]; then
        log_info "Dry run: Skipping Prometheus Node Exporter installation."
        return
    fi

   #$# # Dynamically fetch the latest Node Exporter version
   NODE_EXPORTER_VERSION=$(curl -s https://api.github.com/repos/prometheus/node_exporter/releases/latest | jq -r '.tag_name') || error_exit "Failed to fetch Node Exporter version."
    NODE_EXPORTER_URL="https://github.com/prometheus/node_exporter/releases/download/${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION:1}.linux-amd64.tar.gz"
    NODE_EXPORTER_TARBALL="node_exporter-${NODE_EXPORTER_VERSION:1}.linux-amd64.tar.gz"
    NODE_EXPORTER_DIR="node_exporter-${NODE_EXPORTER_VERSION:1}.linux-amd64"
    # Create system group and user
    sudo groupadd workerGroup &>/dev/null || true
    sudo useradd -g workerGroup nodeExporterUser &>/dev/null || true

    TEMP_NODE_EXPORTER_TARBALL="/tmp/$NODE_EXPORTER_TARBALL"
    TEMP_NODE_EXPORTER_DIR="/tmp/$NODE_EXPORTER_DIR"

    wget -q --tries=3 --timeout=15 "$NODE_EXPORTER_URL" -O "$TEMP_NODE_EXPORTER_TARBALL" || error_exit "Failed to download Node Exporter from $NODE_EXPORTER_URL."
    tar -xzf "$TEMP_NODE_EXPORTER_TARBALL" -C /tmp || error_exit "Failed to extract Node Exporter tarball."

    sudo mv "/tmp/${NODE_EXPORTER_DIR}/node_exporter" /usr/bin/ || error_exit "Failed to move node_exporter to /usr/bin/."
    rm -rf "/tmp/${NODE_EXPORTER_DIR}" "$TEMP_NODE_EXPORTER_TARBALL"

    # Create systemd service file
    cat <<EOF | sudo tee /etc/systemd/system/node_exporter.service >/dev/null
[Unit]
Description=Prometheus Node Exporter Metric Exporter Service
Documentation=https://github.com/prometheus/node_exporter
After=network-online.target

[Service]
Type=simple
User=nodeExporterUser
Group=workerGroup
ExecStart=/usr/bin/node_exporter
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload || error_exit "Failed to reload systemd daemon."
    sudo systemctl enable node_exporter &>/dev/null || error_exit "Failed to enable node_exporter service."
    sudo systemctl start node_exporter &>/dev/null || error_exit "Failed to start node_exporter service."

    log_info "Prometheus Node Exporter installed and started successfully."
}

############################################################
# Main Setup Function                                      #
############################################################

setup() {
    # Initialize arrays for options and positional arguments
    local options=()
    local positional_args=()

    # Parse the arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --bypass-docker|--bypass-apache|--bypass-prometheus|--dry-run|--bypass-python)
                options+=("$1")
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            --*)
                error_exit "Unknown option: $1"
                ;;
            *)
                positional_args+=("$1")
                ;;
        esac
        shift
    done

    # Assign positional arguments
    if [[ "${#positional_args[@]}" -lt 3 ]]; then
        usage
        error_exit "Insufficient arguments provided. You must provide doppler_project, doppler_config, and doppler_token."
    fi
    PROJECT="${positional_args[0]}"
    CONFIG="${positional_args[1]}"
    TOKEN="${positional_args[2]}"

    # Assign options to their respective variables
    for option in "${options[@]}"; do
        case "$option" in
        	--bypass--python)
        	    BYPASS_PYTHON=true
        	    ;;
            --bypass-docker)
                BYPASS_DOCKER=true
                ;;
            --bypass-apache)
                BYPASS_APACHE=true
                ;;
            --bypass-prometheus)
                BYPASS_PROMETHEUS=true
                ;;
            --dry-run)
                DRY_RUN=true
                ;;
        esac
    done

    # Input validation for positional arguments
    if [[ -z "$PROJECT" || -z "$CONFIG" || -z "$TOKEN" ]]; then
        error_exit "All three arguments (doppler_project, doppler_config, doppler_token) are required."
    fi

    log_info "Starting setup with Project: $PROJECT, Config: $CONFIG."

    # Collect PIDs for background tasks
    PIDS=()

    # Install Python and dependencies
    if [[ "$BYPASS_PYTHON" = false ]]; then
        install_python_and_dependencies &
        PIDS+=($!)
    else
        log_info "Bypassing Python3 installation as per user request."
    fi

    # Install Docker and Prometheus Node Exporter in parallel if not bypassed
    if [[ "$BYPASS_DOCKER" = false ]]; then
        install_docker &
        PIDS+=($!)
    else
        log_info "Bypassing Docker installation as per user request."
    fi

    if [[ "$BYPASS_PROMETHEUS" = false ]]; then
        install_prometheus_node_exporter &
        PIDS+=($!)
    else
        log_info "Bypassing Prometheus Node Exporter installation as per user request."
    fi

    # Wait for background jobs to finish
    for PID in "${PIDS[@]}"; do
        wait "$PID"
        # shellcheck disable=SC2181
        if [[ $? -ne 0 ]]; then
            error_exit "A background job with PID $PID failed."
        fi
    done

    # Configure Apache if not bypassed
    if [[ "$BYPASS_APACHE" = false ]]; then
        configure_apache
    else
        log_info "Bypassing Apache installation as per user request."
    fi

    log_info "All selected components installed and configured successfully!"
}


############################################################
# Script Entry Point                                       #
############################################################

main "$@"