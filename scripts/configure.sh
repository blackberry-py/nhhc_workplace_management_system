#!/usr/bin/env bash
set -euo pipefail

############################################################
# Constants and Variables                                  #
############################################################
NODE_EXPORTER_VERSION="1.8.2"
NODE_EXPORTER_URL="https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
NODE_EXPORTER_TARBALL="node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
NODE_EXPORTER_DIR="node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64"

############################################################
# Usage                                                    #
############################################################
usage() {
    cat << EOF
Automatically configure a VM with Apache2, Node Exporter, and supporting tools for an application server behind a reverse proxy.

Syntax: $0 [options] doppler_project doppler_config doppler_token

Arguments:
  doppler_project   The project name in the Doppler Secret Management Platform.
  doppler_config    The configuration to use (e.g., prod, dev, staging).
  doppler_token     The Service Token from the Doppler Secrets Management Platform.

Options:
  --bypass-docker     Bypass Docker installation.
  --bypass-apache     Bypass Apache2 installation.
  --bypass-prometheus Bypass Prometheus Node Exporter installation.
  -h | --help         Print this help message.
EOF
}

############################################################
# Helper Functions                                         #
############################################################

error_exit() {
    echo "❌ ERROR: $1" >&2
    exit 1
}

log_info() {
    echo "🔧 $1"
}

log_success() {
    echo "✅ $1"
}

log_step() {
    echo "🛠️ $1"
}

############################################################
# Installation Functions                                   #
############################################################

install_python_and_dependencies() {
    log_step "Installing Python and dependencies..."
    
    # Update and install base packages
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        apache2-utils \
        certbot \
        python3-certbot-apache \
        direnv \
        python3-pip \
        curl \
        libenchant-2-dev \
        gnupg \
        make \
        git
    
    # Add Doppler repository
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' \
        | sudo gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg
    
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" \
        | sudo tee /etc/apt/sources.list.d/doppler-cli.list >/dev/null
    
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends doppler=3.68.0 build-essential
    sudo apt-get clean
    sudo rm -rf /var/lib/apt/lists/*
    
    # Set Doppler token
    {
        echo "export DOPPLER_TOKEN=${TOKEN}"
    } >> ~/.bashrc
    
    log_success "Python3 and dependencies installed."
}

install_docker() {
    log_step "Installing Docker..."
    
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh &>/dev/null
    rm get-docker.sh
    
    if ! getent group docker &>/dev/null; then
        sudo groupadd docker
    fi
    
    sudo usermod -aG docker "$USER"
    newgrp docker
    
    docker pull terrybrooks/netthands:amd64-aug24 &>/dev/null
    
    log_success "Docker installed and user added to docker group."
}

configure_apache() {
    log_step "Configuring Apache..."
    
    sudo a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests &>/dev/null
    sudo ufw allow 'Apache Full' &>/dev/null
    sudo ufw delete allow 'Apache' &>/dev/null || true
    sudo ufw allow 'OpenSSH' &>/dev/null
    sudo ufw enable &>/dev/null || true
    
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
    cat <<EOF | sudo tee /etc/apache2/sites-available/default-ssl.conf >/dev/null
<IfModule mod_ssl.c>
    <VirtualHost *:443>
        ServerName netthandshome.care
        ServerAlias www.netthandshome.care

        SSLEngine on
        SSLCertificateFile /etc/letsencrypt/live/netthandshome.care/fullchain.pem
        SSLCertificateKeyFile /etc/letsencrypt/live/netthandshome.care/privkey.pem
        SSLCertificateChainFile /etc/letsencrypt/live/netthandshome.care/chain.pem

        ProxyPreserveHost On
        ProxyPass / http://127.0.0.1:8080/
        ProxyPassReverse / http://127.0.0.1:8080/
    </VirtualHost>
</IfModule>
EOF

    sudo a2ensite default-ssl &>/dev/null
    sudo systemctl reload apache2 &>/dev/null
    sudo systemctl enable apache2 &>/dev/null
    sudo systemctl start apache2 &>/dev/null
    
    # shellcheck disable=SC1090
    source ~/.bashrc
    
    log_success "Apache2 configured successfully."
}

install_prometheus_node_exporter() {
    log_step "Installing Prometheus Node Exporter..."
    
    sudo groupadd workerGroup &>/dev/null || true
    sudo useradd -g workerGroup nodeExporterUser &>/dev/null || true

    wget -q "$NODE_EXPORTER_URL"
    tar -xvf "$NODE_EXPORTER_TARBALL" &>/dev/null
    sudo mv ./"${NODE_EXPORTER_DIR}"/node_exporter /usr/bin/
    rm -rf "./${NODE_EXPORTER_DIR}" "$NODE_EXPORTER_TARBALL"

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

    sudo systemctl daemon-reload
    sudo systemctl enable node_exporter &>/dev/null
    sudo systemctl start node_exporter &>/dev/null

    log_success "Prometheus Node Exporter installed and started."
}

############################################################
# Main Setup Function                                      #
############################################################
setup() {
    local bypass_docker=false
    local bypass_apache=false
    local bypass_prometheus=false

    while [ $# -gt 0 ]; do
        case "$1" in
            --bypass-docker)
                bypass_docker=true
                ;;
            --bypass-apache)
                bypass_apache=true
                ;;
            --bypass-prometheus)
                bypass_prometheus=true
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
        shift
    done

    install_python_and_dependencies

    if [ "$bypass_apache" = false ]; then
        configure_apache
    fi

    if [ "$bypass_prometheus" = false ]; then
        install_prometheus_node_exporter
    fi

    if [ "$bypass_docker" = false ]; then
        install_docker
    fi

    log_success "All selected components installed and configured successfully!"
}

############################################################
# Script Entry Point                                       #
############################################################

if [ $# -lt 3 ]; then
    usage
    exit 1
fi

PROJECT=$1
CONFIG=$2
TOKEN=$3
shift 3

# Optional: trap cleanup if needed
# trap 'rm -f /tmp/some_temp_file' EXIT

setup "$@"
