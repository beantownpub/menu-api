#!/bin/bash

AUTH=$(echo -e "${API_USERNAME}:${API_PASSWORD}" | base64)

AUTH_HEADER="Authorization: Basic ${AUTH}"


curl \
    -v \
    -s \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    localhost:5004/v1/menu/section/foo | jq .

curl \
    -v \
    -s \
    -d @data.json \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    localhost:5004/v1/menu/section/foo
