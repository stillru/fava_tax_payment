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
	docker push registry.homelab.local:5000/still/fava:latest
	@echo "Docker image built and pushed to registry."
	@echo "Run 'make run' to start the container with default finance directory."
	@echo "Run 'make run-custom' to start the container with a custom finance directory."
	@echo "You can also run 'make help' for more options."
	@echo "To run the container, use 'docker run -p 5000:5000 -v <path_to_finance_dir>:/app fava'."
	@echo "To access the web interface, open http://localhost:5000 in your browser."
	@echo "To stop the container, use 'docker stop <container_id>'."
	@echo "To remove the container, use 'docker rm <container_id>'."
	@echo "To view logs, use 'docker logs <container_id>'."
	@echo "To enter the container's shell, use 'docker exec -it <container_id> /bin/bash'."
	@echo "To view the list of running containers, use 'docker ps'."
	@echo "To view the list of all containers (including stopped ones), use 'docker ps -a'."
	@echo "To remove all stopped containers, use 'docker container prune'."
	@echo "To remove all unused images, use 'docker image prune'."
	@echo "To remove all unused volumes, use 'docker volume prune'."
	@echo "To remove all unused networks, use 'docker network prune'."
	@echo "To remove all unused resources (containers, images, volumes, networks), use 'docker system prune'."
	@echo "To view the Docker documentation, visit https://docs.docker.com/."
	@echo "To view the Sphinx documentation, visit https://www.sphinx-doc.org/en/master/."
	@echo "To view the Beancount documentation, visit https://beancount.github.io/."

# Run Docker container with default finance directory
run:
	docker run -p 5000:5000 -v $(FINANCE_DIR):/bean \
	-e BEANCOUNT_FILE=/bean/year2025.org \
	fava-tax-payment


# Run Docker container with custom finance directory
run-custom:
	@read -p "Enter path to finance directory: " dir; \
	docker run -p 5000:5000 -v $$dir:/app fava