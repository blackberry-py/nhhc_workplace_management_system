FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

ARG USERNAME=vscode
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends libenchant-2-dev
RUN usermod --login ${USERNAME} --move-home --home /home/${USERNAME} vscode && \
    groupmod --new-name ${USERNAME} vscode

EXPOSE 9090
EXPOSE 8000
EXPOSE 9100
