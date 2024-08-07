#!/bin/bash

EMAIL=$1
PASSWORD=$2

# Install Python
if sudo apt-get update && \
   sudo apt-get install -y --no-install-recommends \
   apt-transport-https ca-certificates apache2-utils \
   libmagic1 curl libenchant-2-dev gnupg make git && \
   curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | \
   sudo gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
   echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | \
   sudo tee /etc/apt/sources.list.d/doppler-cli.list && \
   sudo apt-get update && \
   sudo apt-get --no-install-recommends -y install doppler=3.68.0 build-essential && \
   sudo apt-get clean && \
   sudo rm -rf /var/lib/apt/lists/*; then

    echo "🐍 Successfully Installed Python3...moving on to Docker"

    # Install Docker
    if curl -fsSL https://get.docker.com -o get-docker.sh && \
       sudo sh ./get-docker.sh >> /dev/null && \
       sudo groupadd docker 2>/dev/null && \
       echo '🐳 Successfully Installed Docker...Configuring it to be rootless...' && \
       
       sudo usermod -aG docker "$USER" && \
       newgrp docker; then

        echo 'All finished with Docker...moving on to Traefik'

        # Install Traefik
        if TRAEFIK_ADMIN_LOGIN="$(htpasswd -nb admin "$PASSWORD")" && \
           export TRAEFIK_ADMIN_LOGIN && \
           docker pull traefik:1.7-alpine && \
           docker pull terrybrooks/nhhc:aug24; then

            echo '🚦 Successfully Pulled Docker Images for Application and Traefik...'
            
            # Configure Traefik
            if cat <<EOF > traefik.toml
defaultEntryPoints = ["http", "https"]

[entryPoints]
  [entryPoints.dashboard]
    address = ":8080"
    [entryPoints.dashboard.auth]
      [entryPoints.dashboard.auth.basic]
        users = ["$TRAEFIK_ADMIN_LOGIN"]
  [entryPoints.http]
    address = ":80"
    [entryPoints.http.redirect]
      entryPoint = "https"
  [entryPoints.https]
    address = ":443"
    [entryPoints.https.tls]

[api]
entrypoint = "dashboard"

[acme]
email = "$EMAIL"
storage = "acme.json"
entryPoint = "https"
onHostRule = true
  [acme.httpChallenge]
  entryPoint = "http"

[docker]
domain = "netthandshome.care"
watch = true
network = "web"
EOF
            then
                echo 'Traefik.toml file created and configured' 

                # Start Application
                if docker network create web && \
                   touch acme.json && \
                   chmod 600 acme.json; then 

                    echo 'Fully pre-configured the host runtime environment' 

                    if docker run -d \
                       -v /var/run/docker.sock:/var/run/docker.sock \
                       -v $PWD/traefik.toml:/traefik.toml \
                       -v $PWD/acme.json:/acme.json \
                       -p 80:80 \
                       -p 443:443 \
                       -l traefik.frontend.rule=Host:monitor.netthandshome.care \
                       -l traefik.port=8080 \
                       --network web \
                       --name traefik \
                       traefik:1.7-alpine; then 
                       
                        echo 'Traefik Service is Up and Running' 
                        echo 'Create a Docker Compose file and Register Containers With Traefik Service'
                        echo 'Cheers!!'
                        exit 0 
                    else 
                        echo "❌ Unable to Start The Traefik Service"
                        exit 1  
                    fi 
                else 
                    echo "❌ Unable to Finish Final Pre-configuration steps"
                    exit 1  
                fi 
            else
                echo "❌ Unable to Configure Traefik"
                exit 1  
            fi
        else
            echo "❌ Unable to Pull Docker Images"
            exit 1  
        fi
    else
        echo "❌ Unable to Install Docker"
        exit 1
    fi
else
    echo "❌ Unable to Install Python"
    exit 1
fi