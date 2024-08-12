#!/bin/bash

############################################################
# Usage                                                    #
############################################################
usage() {
    cat << EOF
Automatically Configure a VM with Apache2, a Node Exporter, and all the goodies for an application server behind a reverse proxy.

Syntax: configureServer [options] doppler_project doppler_config doppler_token

Arguments:
  doppler_project   The name of the project in the Doppler Secret Management Platform.
  doppler_config    The configuration to use for the VM (e.g., prod, dev, staging).
  doppler_token     The Service Token from the Doppler Secrets Management Platform.

Options:
  --bypass-docker     Bypass the installation of Docker.
  --bypass-apache     Bypass the installation of Apache2.
  --bypass-prometheus Bypass the installation of a Node Exporter for Prometheus.
  -h | --help         Print this help message.
EOF
}

############################################################
# Main program                                             #
############################################################

set -euo pipefail

# Check for required arguments
if [ $# -lt 3 ]; then
    usage
    exit 1
fi

# Define necessary variables
PROJECT=$1
CONFIG=$2
TOKEN=$3
shift 3

NODE_EXPORTER_URL="https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz"
EXPORTER_FILE="node_exporter-1.8.2.linux-amd64.tar.gz"

# Function to install Python and related packages
install_python() {
    echo "🛠️ Installing Python and dependencies..."

    sudo apt-get update
    sudo apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        apache2-utils \
        certbot \
        python3-certbot-apache \
        libmagic1 \
        curl \
        libenchant-2-dev \
        gnupg \
        make \
        git

    # Add Doppler repository
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | \
        sudo gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg

    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | \
        sudo tee /etc/apt/sources.list.d/doppler-cli.list

    sudo apt-get update
    sudo apt-get install -y --no-install-recommends doppler=3.68.0 build-essential
    sudo apt-get clean
    sudo rm -rf /var/lib/apt/lists/*

    {
        echo "export DOPPLER_TOKEN=${TOKEN}"
        echo "export DOPPLER_CONFIG=${CONFIG}"
        echo "export DOPPLER_PROJECT=${PROJECT}"
        echo "export CONTAINER_PATH_EXC="/src/app/"

    } >> ~/.bashrc

    echo "🐍 Successfully installed Python3 and dependencies."
}

# Function to install Docker
install_docker() {
    echo "🛠️ Installing Docker..."

    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh >/dev/null

    if ! getent group docker >/dev/null; then
        sudo groupadd docker
    fi

    sudo usermod -aG docker "$USER"
    newgrp docker

    docker pull terrybrooks/netthands:amd64-aug24

    echo '🐳 Successfully installed Docker. Configuring it to be rootless...'
}

# Function to configure Apache
configure_apache() {
    echo "🛠️ Configuring Apache..."

    sudo a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests >/dev/null 2>&1
    sudo ufw allow 'Apache Full' >/dev/null 2>&1
    sudo ufw delete allow 'Apache' >/dev/null 2>&1
    sudo ufw allow 'OpenSSH' >/dev/null 2>&1
    sudo ufw enable >/dev/null 2>&1

    cat <<EOF | sudo tee /etc/apache2/sites-available/000-default.conf >/dev/null
<VirtualHost *:80>
    ProxyPreserveHost On
    ServerName netthandshome.care
    ServerAlias www.netthandshome.care

    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/
</VirtualHost>
EOF

    cat <<EOF | sudo tee /etc/apache2/sites-available/default-ssl.conf >/dev/null
<IfModule mod_ssl.c>
    <VirtualHost *:443>
        ServerName netthandshome.care
        ServerAlias www.netthandshome.care

        # SSL configuration
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

    sudo a2ensite default-ssl >/dev/null 2>&1
    sudo systemctl reload apache2 >/dev/null 2>&1
    sudo systemctl enable apache2 >/dev/null 2>&1
    sudo systemctl start apache2 >/dev/null 2>&1

    # shellcheck source=/dev/null
    source ~/.bashrc
    echo '✅ Apache2 configured successfully.'
}

# Function to install Prometheus Node Exporter
install_prometheus() {
    echo "🛠️ Installing Prometheus Node Exporter..."

    sudo groupadd workerGroup >/dev/null 2>&1 || true
    sudo useradd -g workerGroup nodeExportrer >/dev/null 2>&1 || true

    wget -q "$NODE_EXPORTER_URL"
    tar -xvf "$EXPORTER_FILE"
    sudo mv ./node_exporter-1.8.2.linux-amd64/node_exporter /usr/bin/
    rm -rf ./node_exporter-1.8.2.linux-amd64 "$EXPORTER_FILE"

    cat <<EOF | sudo tee /etc/systemd/system/node_exporter.service >/dev/null
[Unit]
Description=Prometheus Node Exporter Metric Exporter Service
Documentation=https://github.com/prometheus/node_exporter
After=network-online.target

[Service]
Type=simple
User=nodeExportrer
Group=workerGroup
ExecStart=/usr/bin/node_exporter
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable node_exporter >/dev/null 2>&1
    sudo systemctl start node_exporter >/dev/null 2>&1
    echo '✅ Prometheus Node Exporter installed and started successfully.'
}

# Main setup function
setup() {
    local bypass_docker=false
    local bypass_apache=false
    local bypass_prometheus=false

    # Parse options
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

    # Install components based on the flags
    install_python
    if [ "$bypass_apache" = false ]; then
        configure_apache
    fi

    if [ "$bypass_prometheus" = false ]; then
        install_prometheus
    fi

    if [ "$bypass_docker" = false ]; then
        install_docker
    fi

    echo '🎉 All selected components installed and configured successfully! 🎉'
}

# Run setup with passed options and arguments
setup "$@"
