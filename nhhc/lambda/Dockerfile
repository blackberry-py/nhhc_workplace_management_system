FROM public.ecr.aws/lambda/python:3.12

RUN apt-get update && apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG DOPPLER_TOKEN
ARG DOPPLER_ENV
ARG DOPPLER_PROJECT
ARG DOPPLER_CONFIG
RUN groupadd --system lambda_gr
RUN useradd --home-dir /src/app/  --base-dir /src/app/ -g lambda_grp lambda

COPY --chown=lambda:lambda_grp ./lambda_constraints.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r lambda_constraints.txt


COPY  --chown=lambda:lambda_grp ./DocSealAttestationProcessing/ ${LAMBDA_TASK_ROOT}/

USER lambda


# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]
