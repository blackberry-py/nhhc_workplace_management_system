FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye

ARG USERNAME=vscode
RUN usermod --login ${USERNAME} --move-home --home /home/${USERNAME} vscode && \
    groupmod --new-name ${USERNAME} vscode

EXPOSE 9090
EXPOSE 8000
EXPOSE 9100
