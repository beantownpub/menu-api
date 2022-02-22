.PHONY: all test clean

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
	docker build -t menu_api:$(image_tag) .

build_no_cache:
	docker build -t menu_api . --no-cache=true

publish: build
	docker tag menu_api:$(image_tag) jalgraves/menu_api:$(image_tag)
	docker push jalgraves/menu_api:$(image_tag)

latest: build
	docker tag menu_api:$(image_tag) jalgraves/menu_api:latest
	docker push jalgraves/menu_api:latest

redis:
	docker run -d --name red -p "6379:6379" --restart always redis

clean:
	rm -rf api/__pycache__ || true
	rm .DS_Store || true
	rm api/*.pyc

seed/beantown/sides:
	python3 bin/seed_products.py --env $(env) --location beantown --type sides

seed/beantown/products:
	python3 bin/seed_products.py --env $(env) --location beantown --type products

seed/beantown/categories:
	python3 bin/seed_products.py --env $(env) --location beantown --type categories

seed/beantown: seed/beantown/categories seed/beantown/products seed/beantown/sides

seed/thehubpub/sides:
	python3 bin/seed_products.py --env $(env) --location thehubpub --type sides

seed/thehubpub/products:
	python3 bin/seed_products.py --env $(env) --location thehubpub --type products

seed/thehubpub/categories:
	python3 bin/seed_products.py --env $(env) --location thehubpub --type categories

seed/thehubpub: seed/thehubpub/categories seed/thehubpub/products seed/thehubpub/sides

reset_db: context
	${HOME}/github/helm/scripts/kill_pod.sh ${DATABASE_NAMESPACE} postgres

kill_pod: context
	${HOME}/github/helm/scripts/kill_pod.sh $(env) $(name)

kill_port_forward: context
	${HOME}/github/helm/scripts/stop_port_forward.sh $(port)

restart: kill_pod kill_port_forward
