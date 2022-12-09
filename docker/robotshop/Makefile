SHELL := bash

include ../../config.mk

BASE_PATH := .
ROBOTSHOP_COMPOSE_FILE := ./std-dmon.yml
ROBOTSHOP_GITHUB_REPO := https://github.com/instana/robot-shop.git

.SILENT: clone
.PHONY: clone
clone:
	$(info $(H)Cloning instana/robot-shop repository$(R))
	if [[ ! -d "$(BASE_PATH)/robot-shop" ]]; then \
		git clone $(ROBOTSHOP_GITHUB_REPO) $(BASE_PATH)/robot-shop; \
	fi

.SILENT: up
.PHONY: up
up:
	$(info $(H)Starting robotshop + dmon cluster$(R))
	docker-compose -f $(ROBOTSHOP_COMPOSE_FILE) up -d

.SILENT: start
.PHONY: start # start robotshop + dmon cluster
start: clone up

.SILENT: down
.PHONY: down
down:
	$(info $(H)Starting robotshop + dmon cluster$(R))
	docker-compose -f $(ROBOTSHOP_COMPOSE_FILE) down

.SILENT: stop
.PHONY: stop # stop robotshop + dmon cluster
stop: down