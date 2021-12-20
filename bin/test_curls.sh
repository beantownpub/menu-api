#!/bin/bash

AUTH=$(echo -e "${API_USERNAME}:${API_PASSWORD}" | base64)

AUTH_HEADER="Authorization: Basic ${AUTH}"

SECTION=${1}


echo "PATH: /v2/menu/items?location=beantown&is_active=false"

curl \
    -s \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    "localhost:5004/v2/menu/items?location=beantown&is_active=false" | jq .

echo "OLD PATH"

curl \
    -s \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    "localhost:5004/v1/menu/section/${SECTION}/active" | jq .

echo "NEW PATH"

curl \
    -s \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    "localhost:5004/v2/menu/items?location=beantown&category=${SECTION}&is_active=true" | jq .

echo "GET Burgers"

curl \
    -s \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    "localhost:5004/v2/menu/categories/burgers?location=beantown" | jq .

echo "GET Fried pickles"

curl \
    -v \
    -s \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    "localhost:5004/v2/menu/items/fried-pickles" | jq .
