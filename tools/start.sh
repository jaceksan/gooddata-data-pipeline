#!/bin/bash

# run airbyte
docker-compose -f airbyte/docker-compose.yaml up -d

echo "wait airbyte to be ready..."
bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:8001/api/v1/health)" != "200" ]]; do echo "  [`date`] waiting...." && sleep 5; done'

# TODO
