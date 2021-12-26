#!/bin/bash

AUTH=$(echo -e "${API_USERNAME}:${API_PASSWORD}" | base64)

AUTH_HEADER="Authorization: Basic ${AUTH}"

LOCATION=${1}
SECTION=${2}

function getActiveSection {
    echo "getActiveSection | Location: ${1} Category: ${2}"
    curl \
        -s \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v2/menu/items?location=${1}&category=${2}&is_active=true" | jq .
}

function getAllCategories {
    echo "getAllCategories | Location: ${1}"
    curl \
        -s \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v2/menu/categories?location=${1}" | jq .
}

function getAllActiveCategories {
    echo "getAllActiveCategories | Location: ${1}"
    curl \
        -s \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v2/menu/categories?location=${1}&is_active=true" | jq .
}

function getAllActiveSides {
    echo "getAllActiveCategories | Location: ${1}"
    curl \
        -s \
        -v \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v2/menu/sides?location=${1}" | jq .
}

function createSide {
    echo "createSide | Location: ${1}"
    curl \
        -s \
        -v \
        -d @tmp.json \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v2/menu/sides" | jq .
}

getAllActiveCategories "${LOCATION}" "${SECTION}"
