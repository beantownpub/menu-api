.PHONY: all test clean

env ?= dev
pg_host ?= $(shell docker inspect pg | jq .[0].NetworkSettings.Networks.bridge.IPAddress || echo "no-container")
tag ?= $(shell yq eval '.info.version' swagger.yaml)

ifeq ($(env),dev)
	pg_host = ${POSTGRES_IP}
	pg_port = 32432
else
	pg_host = postgres.default.svc.cluster.local
	pg_port = 5432
endif

compile:
		pip-compile requirements.in

build:
		@echo "\033[1;32m. . . Building Menu API image . . .\033[1;37m\n"
		docker build -t menu_api:$(tag) .

build_no_cache:
		docker build -t menu_api . --no-cache=true

publish: build
		docker tag menu_api:$(tag) jalgraves/menu_api:$(tag)
		docker push jalgraves/menu_api:$(tag)

latest: build
		docker tag menu_api:$(tag) jalgraves/menu_api:latest
		docker push jalgraves/menu_api:latest

start: stop
		@echo "\033[1;32m. . . Starting Menu API container . . .\033[1;37m\n"
		docker run \
			--name menu_api \
			--restart always \
			-p "5004:5004" \
			-e DB_NAME=${FOOD_DB} \
			-e DB_USER=${DB_USER} \
			-e DB_PWD=${DB_PWD} \
			-e DB_HOST=$(pg_host) \
			-e API_USER_PWD=${API_PW} \
			-e API_USER=${API_USER} \
			menu_api

stop:
		docker rm -f menu_api || true

kill_pod:
		kubectl get pods |  grep menu-api | cut -f 1 -d " " | xargs kubectl delete pod

redis:
		docker run -d --name red -p "6379:6379" --restart always redis

clean:
		rm -rf api/__pycache__ || true
		rm .DS_Store || true
		rm api/*.pyc
