SHELL := bash

include ../../config.mk

BASE_PATH := .
SOCKSHOP_COMPOSE_FILE := ./std-dmon.yml

.SILENT: weave-up
.PHONY: weave-up
weave-up:
	$(info $(H)Starting weave$(R))
	if [ -z `command -v weave` ]; then \
		sudo curl -L git.io/weave -o /usr/local/bin/weave; \
		sudo chmod a+x /usr/local/bin/weave; \
	fi
	weave launch

.SILENT: scope-up
.PHONY: scope-up
scope-up:
	$(info $(H)Starting scope$(R))
	if [ -z `command -v scope` ]; then \
		sudo curl -L git.io/scope -o /usr/local/bin/scope; \
		sudo chmod a+x /usr/local/bin/scope; \
	fi
	scope launch

.SILENT: up
.PHONY: up
up:
	$(info $(H)Starting sockshop + dmon cluster$(R))
	docker-compose -f $(SOCKSHOP_COMPOSE_FILE) up -d

.SILENT: start
.PHONY: start # start sockshop + dmon cluster
start: weave-up scope-up up

.SILENT: weave-down
.PHONY: weave-down
weave-down:
	$(info $(H)Stopping weave$(R))
	weave reset --force
	weave stop

.SILENT: scope-down
.PHONY: scope-down
scope-down:
	$(info $(H)Stopping scope$(R))
	scope stop

.SILENT: down
.PHONY: down
down:
	$(info $(H)Stopping sockshop + dmon cluster$(R))
	docker-compose -f $(SOCKSHOP_COMPOSE_FILE) down

.SILENT: stop
.PHONY: stop # stop sockshop + dmon cluster
stop: down scope-down weave-down
