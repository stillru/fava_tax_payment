# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docsource
DOCSBUILDDIR  = docs
BUILDDIR      = .

.PHONY: help clean html

all: clean html md build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(DOCSBUILDDIR)" $(SPHINXOPTS) $(SPHINXBUILDARGS)

clean_doc:
	rm -rfv $(BUILDDIR)/*

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(DOCSBUILDDIR)" $(SPHINXOPTS) $(SPHINXBUILDARGS)

md:
	@$(SPHINXBUILD) -M text "$(SOURCEDIR)" "$(DOCSBUILDDIR)" $(SPHINXOPTS) $(SPHINXBUILDARGS)

clean:
	rm -rfv $(BUILDDIR)/dist $(BUILDDIR)/build $(BUILDDIR)/*.egg-info/

build: clean
	python3 setup.py bdist_wheel
	docker build -t fava-tax-payment .

run:
	docker run -p 5000:5000 -v $(FINANCE_DIR):/app fava-tax-payment

# Allow overriding the finance directory path
run-custom:
	@read -p "Enter path to finance directory: " dir; \
	docker run -p 5000:5000 -v $$dir:/app fava-tax-payment