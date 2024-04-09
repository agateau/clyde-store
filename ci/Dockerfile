# Docker image to test Clyde packages in a minimalist environment
FROM ubuntu:22.04

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        git \
        curl \
        python3 \
        ca-certificates

COPY . /opt/ci

RUN useradd --create-home user
USER user
WORKDIR /home/user

CMD bash
