.PHONY: all test clean

export MAKE_PATH ?= $(shell pwd)
export SELF ?= $(MAKE)
SHELL := /bin/bash

MAKE_FILES = ${MAKE_PATH}/Makefile

name ?= menu-api
env ?= dev
port ?= 5004
tag ?= $(shell yq eval '.info.version' swagger.yaml)
hash = $(shell git rev-parse --short HEAD)

ifeq ($(env),dev)
	image_tag = $(tag)-$(hash)
	context = ${DEV_CONTEXT}
	namespace = ${DEV_NAMESPACE}
else ifeq ($(env),prod)
    image_tag = $(tag)
	context = ${PROD_CONTEXT}
	namespace = ${PROD_NAMESPACE}
else
	env := dev
endif

context:
	kubectl config use-context $(context)

compile:
	pip-compile requirements.in

build:
	@echo "\033[1;32m. . . Building Menu API image . . .\033[1;37m\n"
	docker build --platform linux/x86_64 -t menu-api:$(image_tag) .

build_no_cache:
	docker build -t menu-api . --no-cache=true

publish: build
	docker tag menu-api:$(image_tag) jalgraves/menu-api:$(image_tag)
	docker push jalgraves/menu-api:$(image_tag)

latest: build
	docker tag menu-api:$(image_tag) jalgraves/menu-api:latest
	docker push jalgraves/menu-api:latest

redis:
	docker run -d --name red -p "6379:6379" --restart always redis

clean:
	rm -rf api/__pycache__ || true
	rm .DS_Store || true
	rm api/*.pyc

## Seed Beantown menu sides
seed/beantown/sides:
	python3 bin/seed_products.py --env $(env) --location beantown --type sides

## Seed Beantown products
seed/beantown/products:
	python3 bin/seed_products.py --env $(env) --location beantown --type products

## Seed Beantown menu categories
seed/beantown/categories:
	python3 bin/seed_products.py --env $(env) --location beantown --type categories

## Seed full Beantown menu
seed/beantown: seed/beantown/categories seed/beantown/products seed/beantown/sides

## Seed Hub Pub menu sides
seed/thehubpub/sides:
	python3 bin/seed_products.py --env $(env) --location thehubpub --type sides

seed/thehubpub/products:
	python3 bin/seed_products.py --env $(env) --location thehubpub --type products

seed/thehubpub/categories:
	python3 bin/seed_products.py --env $(env) --location thehubpub --type categories

## Seed full Hub Pub menu
seed/thehubpub: seed/thehubpub/categories seed/thehubpub/products seed/thehubpub/sides

## Reset the database
reset_db: context
	${HOME}/github/helm/scripts/kill_pod.sh ${DATABASE_NAMESPACE} postgres

kill_pod: context
	${HOME}/github/helm/scripts/kill_pod.sh $(env) $(name)

kill_port_forward: context
	${HOME}/github/helm/scripts/stop_port_forward.sh $(port)

restart: kill_pod kill_port_forward

## Show available commands
help:
	@printf "Available targets:\n\n"
	@$(SELF) -s help/generate | grep -E "\w($(HELP_FILTER))"
	@printf "\n\n"

help/generate:
	@awk '/^[a-zA-Z\_0-9%:\\\/-]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = $$1; \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			gsub("\\\\", "", helpCommand); \
			gsub(":+$$", "", helpCommand); \
			printf "  \x1b[32;01m%-35s\x1b[0m %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKE_FILES) | sort -u
