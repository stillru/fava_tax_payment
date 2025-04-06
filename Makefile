# Minimal Makefile for Sphinx documentation and project build

# Variables (overridable from command line or environment)
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docsource
DOCSBUILDDIR  = docs
BUILDDIR      = .
FINANCE_DIR   = $(shell pwd)/..

.PHONY: help clean clean_doc html md build run run-custom deps

# Default target
all: clean clean_doc build html md

# Help
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(DOCSBUILDDIR)" $(SPHINXOPTS)

# Install dependencies
deps:
	pip install -r requirements.txt
	pip install sphinx sphinx-rtd-theme beancount

# Clean documentation directory
clean_doc:
	rm -rf $(DOCSBUILDDIR)/*

# Build HTML documentation
html: deps
	touch "$(DOCSBUILDDIR)/.nojekyll"
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(DOCSBUILDDIR)" $(SPHINXOPTS)

# Build Markdown/Text documentation
md: deps
	@$(SPHINXBUILD) -b text "$(SOURCEDIR)" "$(DOCSBUILDDIR)/text" $(SPHINXOPTS)

# Clean build artifacts
clean:
	rm -rf $(BUILDDIR)/dist $(BUILDDIR)/build $(BUILDDIR)/*.egg-info/

# Build and install package, then build Docker image
build: clean deps
	python3 setup.py bdist_wheel
	pip install --force-reinstall dist/*.whl  # Устанавливаем в текущее окружение
	docker build -t fava .
	docker image tag fava:latest registry.homelab.local:5000/still/fava:latest

# Run Docker container with default finance directory
run:
	docker run -p 5000:5000 -v $(FINANCE_DIR):/bean \
	-e BEANCOUNT_FILE=/bean/year2025.org \
	fava-tax-payment


# Run Docker container with custom finance directory
run-custom:
	@read -p "Enter path to finance directory: " dir; \
	docker run -p 5000:5000 -v $$dir:/app fava