# Use a Python 3.12 base image
FROM python:3.12-slim
LABEL maintainer="Terry Brooks, Jr."

# Install necessary dependencies and Doppler CLI
RUN apt update && apt upgrade -y && apt install -y \
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
    git

# Install Doppler CLI
RUN curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | \
    gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | \
    tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler=3.69.0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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

# Copy and install requirements
COPY --chown=nhhc_app:nhhc ./requirements.txt ./requirements.txt
COPY --chown=nhhc_app:nhhc ./Makefile /src/app/Makefile

# Copy the application code
COPY --chown=nhhc_app:nhhc nhhc/ /src/app/
RUN touch /src/.attestation_sweeper.log && chmod 777 /src/.attestation_sweeper.log
ADD --chown=nhhc_app:nhhc ./scripts/attestation_sweeper.sh /src/attestation_sweeper.sh
RUN chmod +x /src/attestation_sweeper.sh

# Install application dependencies
RUN pip install -r ./requirements.txt

# Set up Doppler directory permissions
RUN mkdir -p /src/app/.doppler && \
    chown nhhc_app:nhhc /src/app/.doppler && \
    chmod 775 /src/app/.doppler

# Copy additional files
COPY --chown=nhhc_app:nhhc ./postgres_ssl.crt /src/postgres_ssl.crt


# Set the shell to bash
SHELL ["/bin/bash", "-c"]

# Set up cron job for attestation sweeper
RUN echo "0 23 * * sat /bin/bash /src/attestation_sweeper.sh" > /etc/cron.d/attestation_sweeper && \
    chmod 0644 /etc/cron.d/attestation_sweeper

# Use non-root user
USER nhhc_app

# Healthcheck command
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7772/status || exit 1

# Command to run the Gunicorn server
CMD ["gunicorn", "--workers=3", "--threads=2", "nhhc.wsgi:application", "-b", ":7772"]