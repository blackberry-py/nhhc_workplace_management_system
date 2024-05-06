FROM python:3.12-slim-bullseye as builder

RUN apt-get update && apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl libenchant-2-dev gnupg make git && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get --no-install-recommends -y install doppler=3.68.0 build-essential  && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



WORKDIR /src/app/
EXPOSE 8080
ARG DOPPLER_TOKEN
ARG DOPPLER_ENV
ARG DOPPLER_PROJECT
ARG DOPPLER_CONFIG

RUN groupadd --system nhhc
RUN useradd --home-dir /src/app/  --base-dir /src/app/ -g nhhc nhhc_app
COPY --chown=nhhc_app:nhhc ./requirements.txt ./requirements.txt
COPY --chown=nhhc_app:nhhc /nhhc/Makefile /src/app/Makefile

COPY --chown=nhhc_app:nhhc nhhc/ /src/app/
RUN make install
RUN mkdir -p src/app/.doppler
RUN chown nhhc_app:nhhc src/app/.doppler
RUN chmod 775 src/app/.doppler

ENTRYPOINT [ "make", "start"]
