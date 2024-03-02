FROM python:3.11.2-slim-bullseye as builder

RUN apt-get update && \
    apt-get upgrade --yes \
    apt-get install --yes dumb-init

WORKDIR /src/app/

ENV VIRTUALENV=/Users/terry-brookls/Documents/Github/NettHands/.env-nett-hands
RUN python3 -m venv $VIRTUALENV
ENV PATH="$VIRTUALENV/bin:$PATH"


COPY --chown=nhhc_app pyproject.toml requirements.txt ./



COPY --chown=nhhc_app entrypoint.sh ./
RUN chmod +x init.sh

COPY --chown=nhhc_app nhhc/ /src/app/

RUN useradd --create-home nhhc_app
USER nhhc_app

ENTRYPOINT ["source" "${VIRTUALENV}/bin/activate" , "&&", "python", "/src/app/manage.py","runserver", "0.0.0.0:1357" ]
