#!/bin/bash

AUTH=$(echo -e "${API_USERNAME}:${API_PASSWORD}" | base64)

AUTH_HEADER="Authorization: Basic ${AUTH}"

LOCATION=${1}
TABLE_NAME=${2}

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
        -v \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v3/menu/categories?location=beantown&with_items=true" | jq .
}

function getAllActiveCategories {
    echo "getAllActiveCategories | Location: ${1}"
    curl \
        -s \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v3/menu/categories?location=${1}&is_active=true" | jq .
}

function getAllInActiveCategories {
    echo "getAllActiveCategories | Location: ${1}"
    curl \
        -s \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v3/menu/categories?location=${1}&is_active=false" | jq .
}

function getAllActiveAppetizers {
    echo "getAllActiveAppetizers | Location: ${1}"
    curl \
        -s \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v3/menu/categories?location=${1}&is_active=true&category=appetizers" | jq .
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

function getAllProducts {
    echo "getAllCategories | Location: ${1}"
    curl \
        -s \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v3/menu/food_items?location=${1}" | jq .
}

function getOldMenu {

    echo "OLD MENU | Location: ${1}"
    curl \
        -s \
        -v \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v2/menu/categories?is_active=true&location=beantown" | jq .
}

function getMenu {
    echo "getMenu | Location: ${1}"
    curl \
        -s \
        -v \
        -H "${AUTH_HEADER}" \
        -H "Content-Type: application/json" \
        "localhost:5004/v3/menu?location=${1}" | jq .
}

if [[ "${TABLE_NAME}" = "items" ]]; then
    getAllProducts "${LOCATION}"
fi

if [[ "${TABLE_NAME}" = "categories" ]]; then
    getAllCategories "${LOCATION}"
fi

if [[ "${TABLE_NAME}" = "menu" ]]; then
    getMenu "${LOCATION}"
fi
