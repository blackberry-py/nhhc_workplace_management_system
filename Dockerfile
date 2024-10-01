# Use a Python 3.12 base image
FROM python:3.12-slim
MAINTAINER Terry Brooks, Jr. 

# Install necessary dependencies and Doppler CLI
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    apache2-utils \
    curl  \
    gnupg \
    cron \
    libmagic1 \
    libssl-dev \
    libenchant-2-dev\
    make=4.3-4.1 \
    git= 1:2.39.2-1.1 && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler=3.69.0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*



















































































































































































































































































































































    essary ports
EXPOSE 7772

# Set environment variables
ARG TOKEN=${NHHC_DT}
ARG DOPPLER_PROJECT='nhhc'
ARG DOPPLER_CONFIG='prod'
ENV DOPPLER_TOKEN=${TOKEN}
ENV DOPPLER_PROJECT=${DOPPLER_PROJECT}
ENV DOPPLER_CONFIG=${DOPPLER_CONFIG}

# Create necessary groups and users
RUN groupadd --system celery && \
    useradd -g celery celery && \
    groupadd --system nhhc && \
    useradd --home-dir /src/app --no-create-home -g nhhc nhhc_app

# Copy and install requirementsN
COPY --chown=nhhc_app:nhhc ./docker_requirements.txt ./requirements.txt
COPY --chown=nhhc_app:nhhc ./nhhc/Makefile /src/app/Makefile

# Copy the application code
COPY --chown=nhhc_app:nhhc nhhc/ /src/app/
RUN touch /src/.attestation_sweeper.log && chmod 777 /src/.attestation_sweeper.log
ADD --chown=nhhc_app:nhhc ./attestation_sweeper.sh /src/attestation_sweeper.sh
RUN chmod 0644 /src/attestation_sweeper.sh
# Install application dependencies
RUN pip install -r ./requirements.txt
RUN pip install -r ./requirements.txt

# Set up Doppler directory permissions
RUN mkdir -p /src/app/.doppler && \
    chown nhhc_app:nhhc /src/app/.doppler && \
    chmod 775 /src/app/.doppler

COPY --chown=nhhc_app:nhhc ./postgres_ssl.crt  /src/postgres_ssl.crt
COPY --chown=nhhc_app:nhhc ./prometheus.yml  /src/prometheus.yml
USER nhhc_app

# Set the shell to bash
SHELL ["/bin/bash", "-c"]
RUN cat <<EOF | tee /etc/crontab > /dev/null
0 23 * * sat bash /src/attestation_sweeper.sh
EOF
USER nhhc_app

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "" ]
# Command to run the Gunicorn server
CMD ["gunicorn", "--workers=3", "--threads=2", "nhhc.wsgi:application", "-b", ":7772"]
