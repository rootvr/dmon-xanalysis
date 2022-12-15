SHELL := bash

include ../../config.mk

BASE_PATH := .
LAKESIDE_COMPOSE_FILE := ./lakesidemutual/docker-compose.prod.yml
LAKESIDE_GITHUB_REPO := https://github.com/microservice-api-patterns/lakesidemutual

.SILENT: clone
.PHONY: clone
clone:
	$(info $(H)Cloning instana/robot-shop repository$(R))
	if [[ ! -d "$(BASE_PATH)/lakesidemutual" ]]; then \
		git clone $(LAKESIDE_GITHUB_REPO) $(BASE_PATH)/lakesidemutual; \
	fi

.SILENT: dmon-up
.PHONY: dmon-up
dmon-up:
	PHYSICAL_IFACE=`ip a | grep -P "^[0-9]+: br-" | cut -d" " -f2 | sed "s/://"`
	docker run -d --name rootvr_dmon -v /var/run/docker.sock:/var/run/docker.sock --network=host rootvr/dmon:latest \
		-t 5 -n lakesidemutual_default -i $$PHYSICAL_IFACE -r localhost:6379

.SILENT: up
.PHONY: up
up:
	$(info $(H)Starting lakeside + dmon cluster$(R))
	docker-compose -f $(LAKESIDE_COMPOSE_FILE) up -d

.SILENT: start
.PHONY: start # start lakeside + dmon cluster
.ONESHELL:
start: clone up dmon-up

.SILENT: down
.PHONY: down
down:
	$(info $(H)Stopping lakeside + dmon cluster$(R))
	docker container rm -f rootvr_dmon
	docker-compose -f $(LAKESIDE_COMPOSE_FILE) down

.SILENT: stop
.PHONY: stop # stop lakeside + dmon cluster
stop: down
