SHELL := /bin/bash

PYTHON ?= python3
VENV := venv
BIN := $(VENV)/bin

# The documentation site's Terraform stack (terraform/docs). The account id is read from the
# caller's AWS credentials when a target needs it, never written into this public repository.
TF := terraform -chdir=terraform/docs
AWS_ACCOUNT_ID = $(shell aws sts get-caller-identity --query Account --output text)
TF_STATE_BUCKET = $(AWS_ACCOUNT_ID)-terraform-tfstate-smarter

.PHONY: all help init check-python test coverage typecheck build clean \
	python-requirements lint analyze pre-commit-init pre-commit-run \
	sphinx-build sphinx-linkcheck sphinx-publish terraform-init terraform-plan terraform-apply \
	release-dry-run release

# Default target executed when no arguments are given to make.
all: help

# ---------------------------------------------------------
# Development
# ---------------------------------------------------------
# this repository's own virtual environment, from its own pinned requirements: never another project's venv.
init:
	@echo "==============================================================================="
	@echo "Creating $(VENV) from requirements/local.txt, installing the package, and the git hooks ..."
	@echo "==============================================================================="
	make check-python
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements/local.txt
	$(BIN)/pip install -e . --no-deps
	make pre-commit-init

# requirements/in/*.in, each starting with -r constraints.in, compile into the pinned requirements/*.txt.
# --no-strip-extras keeps extras such as coverage[toml], which pip-tools 8 would drop.
python-requirements:
	@echo "==============================================================================="
	@echo "Compiling and updating Python dependency files using pip-compile ..."
	@echo "==============================================================================="
	$(BIN)/pip install --upgrade "pip-tools>=7.6.1"
	$(BIN)/pip-compile --upgrade --no-strip-extras requirements/in/base.in -o requirements/base.txt
	$(BIN)/pip-compile --upgrade --no-strip-extras requirements/in/local.in -o requirements/local.txt
	$(BIN)/pip install -r requirements/local.txt
	$(BIN)/pip install -e . --no-deps

check-python:
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo >&2 "$(PYTHON) is not installed. Aborting."; exit 1; }
	@$(PYTHON) -c "import sys; sys.exit(sys.version_info < (3, 10))" || { \
		echo >&2 "smarter-types needs Python 3.10 or newer. $(PYTHON) is $$($(PYTHON) --version)."; exit 1; }

test:
	@echo "==============================================================================="
	@echo "Running the tests ..."
	@echo "==============================================================================="
	$(BIN)/python -m pytest

coverage:
	@echo "==============================================================================="
	@echo "Running the tests with a coverage report ..."
	@echo "==============================================================================="
	$(BIN)/coverage run -m pytest
	$(BIN)/coverage report
	$(BIN)/coverage xml

typecheck:
	@echo "==============================================================================="
	@echo "Checking the package's type annotations with mypy ..."
	@echo "==============================================================================="
	$(BIN)/mypy

build:
	@echo "==============================================================================="
	@echo "Building the sdist and wheel into dist/, and checking them with twine ..."
	@echo "==============================================================================="
	rm -rf dist
	$(BIN)/python -m build
	$(BIN)/twine check --strict dist/*

clean:
	@echo "==============================================================================="
	@echo "Removing build, test and coverage artifacts ..."
	@echo "==============================================================================="
	rm -rf build dist docs/build .pytest_cache .coverage coverage.xml htmlcov node_modules
	find . -name __pycache__ -type d -prune -not -path "./$(VENV)/*" -exec rm -rf {} +

# ---------------------------------------------------------
# Code Management
# ---------------------------------------------------------
lint:
	make pre-commit-run

analyze:
	@echo "==============================================================================="
	@echo "Generating code analysis report using cloc ..."
	@echo "==============================================================================="
	cloc . --vcs=git

pre-commit-init:
	@echo "==============================================================================="
	@echo "Installing and configuring pre-commit ..."
	@echo "==============================================================================="
	$(BIN)/pre-commit install
	$(BIN)/pre-commit autoupdate

pre-commit-run:
	@echo "==============================================================================="
	@echo "Running pre-commit hooks on all files ..."
	@echo "==============================================================================="
	$(BIN)/pre-commit run --all-files

# ---------------------------------------------------------
# Sphinx documentation: docs.smarter-types.smarter.sh
# ---------------------------------------------------------
sphinx-build:
	@echo "==============================================================================="
	@echo "Building the Sphinx documentation into docs/build/html, warnings as errors ..."
	@echo "==============================================================================="
	rm -rf docs/build
	$(BIN)/sphinx-build -W --keep-going -b html -d docs/build/doctrees docs/source docs/build/html

sphinx-linkcheck:
	$(BIN)/sphinx-build -b linkcheck -d docs/build/doctrees docs/source docs/build/linkcheck

# the bucket and distribution come from the Terraform stack's outputs (make terraform-apply).
sphinx-publish: sphinx-build
	@echo "==============================================================================="
	@echo "Publishing docs/build/html to https://docs.smarter-types.smarter.sh/ ..."
	@echo "==============================================================================="
	BUCKET=$$($(TF) output -raw bucket_name) && \
	DISTRIBUTION=$$($(TF) output -raw distribution_id) && \
	aws s3 sync docs/build/html "s3://$$BUCKET/" --delete --exclude ".doctrees/*" --exclude ".buildinfo" && \
	aws cloudfront create-invalidation --distribution-id "$$DISTRIBUTION" --paths "/*" --query Invalidation.Id --output text

# ---------------------------------------------------------
# Terraform: the documentation site's AWS resources (terraform/docs)
# ---------------------------------------------------------
terraform-init:
	$(TF) init -backend-config="bucket=$(TF_STATE_BUCKET)"

# writes the plan to terraform/docs/tfplan, which terraform-apply applies exactly.
terraform-plan:
	$(TF) plan -out=tfplan

terraform-apply:
	$(TF) apply tfplan
	rm -f terraform/docs/tfplan

# ---------------------------------------------------------
# Release
# ---------------------------------------------------------
# main makes a release, published to TestPyPI then PyPI. RELEASE_BRANCH=alpha or beta makes a
# prerelease, published to TestPyPI only. See .github/workflows/release.yml.
RELEASE_BRANCH ?= main

release-dry-run:
	@echo "==============================================================================="
	@echo "Starting the Release workflow on $(RELEASE_BRANCH) as a dry run: CI, then the next version ..."
	@echo "==============================================================================="
	gh workflow run release.yml --ref $(RELEASE_BRANCH) -f dry_run=true
	@echo "Follow it with: gh run watch"

release:
	@echo "==============================================================================="
	@echo "Starting the Release workflow on $(RELEASE_BRANCH): CI, release, TestPyPI and PyPI ..."
	@echo "==============================================================================="
	gh workflow run release.yml --ref $(RELEASE_BRANCH) -f dry_run=false
	@echo "Follow it with: gh run watch"

help:
	@echo '===================================================================='
	@echo 'init                   - Create venv from requirements/local.txt, install the package and the git hooks'
	@echo 'python-requirements    - Compile requirements/in/*.in into the pinned requirements/*.txt, and install them'
	@echo 'check-python           - Verify that Python 3.10 or newer is installed'
	@echo 'test                   - Run the tests'
	@echo 'coverage               - Run the tests with a coverage report, and write coverage.xml'
	@echo 'typecheck              - Check the type annotations with mypy'
	@echo 'build                  - Build the sdist and wheel into dist/, and check them'
	@echo 'clean                  - Remove build, test and coverage artifacts'
	@echo '<************************** Code Management **************************>'
	@echo 'lint                   - Run all code linters and formatters'
	@echo 'analyze                - Generate code analysis report using cloc'
	@echo 'pre-commit-init        - Install and configure pre-commit'
	@echo 'pre-commit-run         - Run all pre-commit hooks on all files'
	@echo '<************************** Documentation **************************>'
	@echo 'sphinx-build           - Build the Sphinx docs into docs/build/html, warnings as errors'
	@echo 'sphinx-linkcheck       - Check every external link in the docs'
	@echo 'sphinx-publish         - Build the docs, upload them to S3 and invalidate CloudFront'
	@echo 'terraform-init         - Initialize the docs site stack (terraform/docs) and its state'
	@echo 'terraform-plan         - Plan changes to the docs site AWS resources, into terraform/docs/tfplan'
	@echo 'terraform-apply        - Apply terraform/docs/tfplan'
	@echo '<************************** Release **************************>'
	@echo 'release-dry-run        - Run the Release workflow as a dry run: CI, then the next version'
	@echo 'release                - Release and publish: CI, tag, GitHub release, TestPyPI, PyPI (RELEASE_BRANCH)'
	@echo '===================================================================='
