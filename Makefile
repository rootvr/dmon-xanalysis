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
clean: clean-dmon clean-wgen clean-xdriver clean-docker clean-test-env

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

.SILENT: clean-test-env
.PHONY: clean-test-env # clean test env
.ONESHELL:
clean-test-env:
	$(info $(H)Cleaning test env$(R))
	cd ./fdriver
	poetry env remove --all

# ----- DOCKER -----

.SILENT: clean-docker
.PHONY: clean-docker # clean docker host env
clean-docker:
	$(info $(H)Cleaning docker host env$(R))
	docker system prune -f --volumes

# ----- APPLICATIONS -----

.SILENT: rs-start
.PHONY: rs-start # start robotshop + dmon cluster
rs-start: build
	$(MAKE) --no-print-directory -C $(ROBOTSHOP_DOCKER_PATH) start

.SILENT: rs-stop
.PHONY: rs-stop # stop robotshop + dmon cluster
rs-stop:
	$(MAKE) --no-print-directory -C $(ROBOTSHOP_DOCKER_PATH) stop

# ----- TESTING -----

.SILENT: run-test
.PHONY: run-test # run a test
.ONESHELL:
run-test:
	$(info $(H)Building poetry virtual env for testing$(R))
	cd ./fdriver
	poetry install
	poetry run bash -c "cd .. && python ./fdriver/src/main.py $(ARGS)"
