# Define Python version as argument
ARG PYTHON_VERSION=3.11.3

# Base image
FROM python:${PYTHON_VERSION}-slim-bullseye

# Metadata
LABEL version="1.0" \
      description="Python ${PYTHON_VERSION} application" \
      maintainer="mickzeller@gmail.com"

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install curl and ca-certificates in a single RUN instruction
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    curl \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* ./

ARG INSTALL_DEV=true

RUN BASIC_CMD="poetry install --no-root"; \
    if [ "$INSTALL_DEV" == "true" ]; \
    then FINAL_CMD=$BASIC_CMD; \
    else FINAL_CMD="$BASIC_CMD --only main"; \
    fi && \
    bash -c $FINAL_CMD

COPY . .

CMD ["python", "./app/virtual_assistant.py"]
