# Use a custom Python 3.12 base image
FROM terrybrooks/carenett
LABEL maintainer="Terry Brooks, Jr."

# Expose Flower port
EXPOSE 9005

# Set environment variables
ENV CELERY_APP=nhhc

USER root
# Create necessary groups and users
RUN useradd -g celery flower


# Switch to non-root user for security
USER flower

# Set the shell to bash
SHELL ["/bin/bash", "-c"]


# Set entrypoint to Doppler with Celery commands
ENTRYPOINT ["doppler", "run", "--"]

# Default CMD to run Celery Flower
CMD ["celery", "-A", ${CELERY_APP}, "flower", "--port=9005"]