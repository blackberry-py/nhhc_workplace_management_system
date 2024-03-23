FROM python:3.11.2-slim-bullseye as builder

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes curl


WORKDIR /src/app/
EXPOSE 8080

ENV VIRTUALENV=/Users/terry-brookls/Documents/Github/NettHands/.env-nett-hands
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
&& ls -a $HOME
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

COPY --chown=nhhc_app requirements.txt ./requirements.txt
RUN uv install -r ./requirements.txt

COPY --chown=nhhc_app nhhc/ /src/app/

RUN useradd --create-home nhhc_app
USER nhhc_app

CMD ["doppler", "run", "--", "gunicorn", "wsgi:application", "--bind", "0.0.0.0:8080"]
