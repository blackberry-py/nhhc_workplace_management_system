FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ARG USERNAME=vscode
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    apache2-utils \
    curl \
    gnupg \
    cron \
    libmagic1 \
    libssl-dev \
    libenchant-2-dev \
    make \
    git && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN usermod --login ${USERNAME} --move-home --home /home/${USERNAME} vscode && \
    groupmod --new-name ${USERNAME} vscode


    