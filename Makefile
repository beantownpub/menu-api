.PHONY: all test clean

env ?= dev
tag ?= $(shell yq eval '.info.version' swagger.yaml)
hash = $(shell git rev-parse --short HEAD)

ifeq ($(env),dev)
	image_tag = $(tag)-$(hash)
else
	image_tag = $(tag)
endif

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
