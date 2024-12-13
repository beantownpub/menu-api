.PHONY: all test clean
SHELL := /bin/bash

port := ${MENU_API_PORT}
log_level ?= ${MENU_API_LOG_LEVEL}

ifeq ($(env),dev)
	kubeconfig = ${DEV_KUBECONFIG}
else ifeq ($(env),prod)
	kubeconfig = ${PROD_KUBECONFIG}
endif

menu/clean:
		rm *.tgz || true

menu/context:
	kubectl config use-context $(context)

## Publish menu-api Helm chart
menu_api/publish:
	cd helm/menu-api && \
		helm package . && \
		cd - && \
		helm repo index . --url https://beantownpub.github.io/helm/ && \
		git add helm/menu-api/

## Deploy menu-api to a cluster
helm/install:
	@echo "\033[1;32m. . . Installing menu-api in $(env) . . .\033[1;37m\n"
	helm upgrade --install menu-api helm/menu-api/ \
		--kubeconfig="${HOME}"/.kube/$(kubeconfig) \
		--namespace $(namespace) \
		--set aws.regionCode=use1 \
		--set global.env=$(env) \
		--set image.tag=$(tag) \
		--set logLevel=$(log_level) \
		--set externalSecrets.enabled=true \
		--debug

menu/template:
	@echo "\033[1;32m. . . Templating menu-api in $(env) . . .\033[1;37m\n"
	cd menu_api && \
	helm template . \
		--name-template=$(name) \
		--set global.env=$(env) \
		--set image.name=$(image) \
		--set image.tag=$(tag) \
		--set logLevel=$(log_level) \
		--debug

## Forward menu-api port
menu_api/port_forward: menu/context
		kubectl port-forward --namespace $(namespace) svc/$(name) $(port):$(port)

menu/stop_pf:
		../scripts/stop_port_forward.sh $(port)

menu/logs:
		../scripts/get_pod_logs.sh $(namespace) $(name)

menu/describe:
		../scripts/describe_pod.sh $(namespace) $(name)

## Delete menu-api pod
menu/kill: menu/context
		./scripts/kill_pod.sh $(namespace) $(name)
