.PHONY: build deploy manifests push test

dc = docker compose

CHART ?= oci://saks01weuacrpgpgo5qvmwo.azurecr.io/amsterdam/helm-generic-application
CHART_VERSION ?= 1.13.0

HELM_RELEASE ?= brpproxy
ENVIRONMENT ?= local
HELM_ARGS = $(CHART) --version $(CHART_VERSION) \
	-f manifests/values.yaml \
	-f manifests/env/${ENVIRONMENT}.yaml \
	--set image.tag=${VERSION}

REGISTRY ?= localhost:5001
REPOSITORY ?= brpproxy/gobstuf
VERSION ?= latest

SERVICE_APP ?= gobstuf-app
SERVICE_TEST ?= gobstuf-test

build:
	$(dc) build $(SERVICE_APP)

push: build
	$(dc) push $(SERVICE_APP)

deploy: manifests
	helm upgrade --install $(HELM_RELEASE) $(HELM_ARGS)

manifests:
	helm template $(HELM_RELEASE) $(HELM_ARGS)

test:
	$(dc) run $(SERVICE_TEST)
