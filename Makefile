SHELL := /bin/bash

.PHONY: venv fmt lint test deploy-aws

venv:
	python3 -m venv .venv && source .venv/bin/activate && pip install -r api/requirements.txt

fmt:
	black . || true
	isort . || true

lint:
	flake8 || true

test:
	pytest -q || true

deploy-aws:
	cd infra/aws && terraform init && terraform apply -auto-approve

plan-aws:
	cd infra/aws && terraform init && terraform plan
