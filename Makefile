SHELL := bash

include config.mk

.SILENT: help
.PHONY: help # print help
help:
	grep '^.PHONY: .* #' $(firstword $(MAKEFILE_LIST)) |\
	sed 's/\.PHONY: \(.*\) # \(.*\)/\1 # \2/' |\
	awk 'BEGIN {FS = "#"}; {printf "%-20s %s\n", $$1, $$2}'

# ----- GIT -----

.SILENT: sync
.PHONY: sync # sync submodules
sync:
	$(info $(H)Syncing git submodules$(R))
	git submodule update --init --recursive --remote

# ----- COMBOS -----

.SILENT: build
.PHONY: build # build all (combo)
build: sync build-dmon build-wgen build-xdriver

.SILENT: clean
.PHONY: clean # clean all (combo)
clean: clean-dmon clean-wgen clean-xdriver clean-docker clean-fdriver clean-alyslib

# ----- TOOLS (build) -----

.SILENT: build-dmon
.PHONY: build-dmon # build dmon
build-dmon:
	$(info $(H)Building dmon docker container$(R))
	$(MAKE) --no-print-directory -C $(DMON_MOD_PATH) clean deps build genimage

.SILENT: build-wgen
.PHONY: build-wgen # build wgen
build-wgen:
	$(info $(H)Building wgen binary$(R))
	$(MAKE) --no-print-directory -C $(WGEN_MOD_PATH) clean deps build install

.SILENT: build-xdriver
.PHONY: build-xdriver # build xdriver
build-xdriver:
	$(info $(H)Building xdriver binary$(R))
	$(MAKE) --no-print-directory -C $(XDRIVER_MOD_PATH) build install

# ----- TOOLS (clean) -----

.SILENT: clean-dmon
.PHONY: clean-dmon # clean dmon
clean-dmon:
	$(info $(H)Cleaning dmon docker container$(R))
	$(MAKE) --no-print-directory -C $(DMON_MOD_PATH) clean delimage

.SILENT: clean-wgen
.PHONY: clean-wgen # clean wgen
clean-wgen:
	$(info $(H)Cleaning wgen binary$(R))
	$(MAKE) --no-print-directory -C $(WGEN_MOD_PATH) clean uninstall

.SILENT: clean-xdriver
.PHONY: clean-xdriver # clean xdriver
clean-xdriver:
	$(info $(H)Cleaning xdriver binary$(R))
	$(MAKE) --no-print-directory -C $(XDRIVER_MOD_PATH) clean uninstall

.SILENT: clean-fdriver
.PHONY: clean-fdriver # clean test env
.ONESHELL:
clean-fdriver:
	$(info $(H)Cleaning test env$(R))
	cd $(FDRIVER_POETRY_PATH)
	poetry env remove --all

.SILENT: clean-alyslib
.PHONY: clean-alyslib # clean test env
.ONESHELL:
clean-alyslib:
	$(info $(H)Cleaning analysis env$(R))
	cd $(ALYSLIB_POETRY_PATH)
	poetry env remove --all

# ----- DOCKER -----

.SILENT: clean-docker
.PHONY: clean-docker # clean docker host env
clean-docker:
	$(info $(H)Cleaning docker host env$(R))
	docker system prune -f --volumes

# ----- APPLICATIONS -----

.SILENT: start-rs
.PHONY: start-rs # start robotshop + dmon cluster
start-rs: build
	$(MAKE) --no-print-directory -C $(ROBOTSHOP_DOCKER_PATH) start

.SILENT: stop-rs
.PHONY: stop-rs # stop robotshop + dmon cluster
stop-rs:
	$(MAKE) --no-print-directory -C $(ROBOTSHOP_DOCKER_PATH) stop

# ----- TESTING -----

.SILENT: run-fdriver
.PHONY: run-fdriver # run a test
.ONESHELL:
run-fdriver:
	$(info $(H)Building poetry virtual env for testing$(R))
	cd $(FDRIVER_POETRY_PATH)
	poetry install
	poetry run bash -c "cd ../.. && python ./src/fdriver/main.py $(ARGS)"

.SILENT: run-alyslib
.PHONY: run-alyslib # activate analysis env
.ONESHELL:
run-alyslib:
	$(info $(H)Building poetry virtual env for analysis$(R))
	cd $(ALYSLIB_POETRY_PATH)
	poetry install
	poetry run bash -c "cd ../../test && jupyter-lab"
