# Contract Risk Analyzer - Docker Makefile
# This Makefile provides easy commands for building and running the application

.PHONY: help build run stop clean logs status health test dev prod

# Default target
.DEFAULT_GOAL := help

# Configuration
IMAGE_NAME := contract-analyzer
TAG := latest
CONTAINER_NAME := contract-analyzer-app
COMPOSE_FILE := docker-compose.yml
ENV_FILE := .env

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Contract Risk Analyzer - Docker Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make build          # Build the Docker image"
	@echo "  make run            # Run the application"
	@echo "  make dev            # Run in development mode"
	@echo "  make prod            # Run in production mode"
	@echo "  make logs            # Show application logs"
	@echo "  make stop            # Stop the application"
	@echo "  make clean           # Clean up everything"

# Environment setup
setup: ## Setup environment from template
	@echo "$(BLUE)Setting up environment...$(NC)"
	@if [ ! -f $(ENV_FILE) ]; then \
		if [ -f env.template ]; then \
			cp env.template $(ENV_FILE); \
			echo "$(YELLOW)Created .env from template. Please update with your configuration.$(NC)"; \
		else \
			echo "$(RED)env.template not found. Please create .env manually.$(NC)"; \
			exit 1; \
		fi \
	else \
		echo "$(GREEN).env file already exists$(NC)"; \
	fi

# Docker image operations
build: setup ## Build the Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@./scripts/docker-build.sh --tag $(TAG) --name $(IMAGE_NAME)

build-no-cache: setup ## Build the Docker image without cache
	@echo "$(BLUE)Building Docker image (no cache)...$(NC)"
	@./scripts/docker-build.sh --tag $(TAG) --name $(IMAGE_NAME) --no-cache

build-push: setup ## Build and push the Docker image
	@echo "$(BLUE)Building and pushing Docker image...$(NC)"
	@./scripts/docker-build.sh --tag $(TAG) --name $(IMAGE_NAME) --push

# Docker run operations
run: setup ## Run the application with Docker
	@echo "$(BLUE)Running Contract Risk Analyzer...$(NC)"
	@./scripts/docker-run.sh --image $(IMAGE_NAME) --tag $(TAG) --name $(CONTAINER_NAME)

run-detached: setup ## Run the application in detached mode
	@echo "$(BLUE)Running Contract Risk Analyzer in detached mode...$(NC)"
	@./scripts/docker-run.sh --image $(IMAGE_NAME) --tag $(TAG) --name $(CONTAINER_NAME) --detach

run-logs: setup ## Run the application and show logs
	@echo "$(BLUE)Running Contract Risk Analyzer with logs...$(NC)"
	@./scripts/docker-run.sh --image $(IMAGE_NAME) --tag $(TAG) --name $(CONTAINER_NAME) --detach --logs

# Docker Compose operations
up: setup ## Start services with Docker Compose
	@echo "$(BLUE)Starting services with Docker Compose...$(NC)"
	@./scripts/docker-compose-up.sh --detach

up-build: setup ## Start services with Docker Compose and build
	@echo "$(BLUE)Starting services with Docker Compose (building)...$(NC)"
	@./scripts/docker-compose-up.sh --detach --build

up-logs: setup ## Start services with Docker Compose and show logs
	@echo "$(BLUE)Starting services with Docker Compose and showing logs...$(NC)"
	@./scripts/docker-compose-up.sh --detach --logs

dev: setup ## Run in development mode (with hot reload)
	@echo "$(BLUE)Running in development mode...$(NC)"
	@./scripts/docker-compose-up.sh --build --logs

prod: setup ## Run in production mode
	@echo "$(BLUE)Running in production mode...$(NC)"
	@./scripts/docker-compose-up.sh --detach --build

# Service management
stop: ## Stop the application
	@echo "$(BLUE)Stopping Contract Risk Analyzer...$(NC)"
	@./scripts/docker-run.sh --stop

stop-compose: ## Stop Docker Compose services
	@echo "$(BLUE)Stopping Docker Compose services...$(NC)"
	@./scripts/docker-compose-up.sh --stop

restart: ## Restart the application
	@echo "$(BLUE)Restarting Contract Risk Analyzer...$(NC)"
	@./scripts/docker-compose-up.sh --restart

# Logs and monitoring
logs: ## Show application logs
	@echo "$(BLUE)Showing application logs...$(NC)"
	@docker logs -f $(CONTAINER_NAME) 2>/dev/null || echo "$(RED)Container not running$(NC)"

logs-compose: ## Show Docker Compose logs
	@echo "$(BLUE)Showing Docker Compose logs...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) logs -f

# Status and health
status: ## Show service status
	@echo "$(BLUE)Service status:$(NC)"
	@./scripts/docker-compose-up.sh --status

health: ## Show service health
	@echo "$(BLUE)Service health:$(NC)"
	@./scripts/docker-compose-up.sh --health

# Cleanup operations
clean: ## Clean up containers and volumes
	@echo "$(BLUE)Cleaning up...$(NC)"
	@./scripts/docker-run.sh --clean

clean-compose: ## Clean up Docker Compose resources
	@echo "$(BLUE)Cleaning up Docker Compose resources...$(NC)"
	@./scripts/docker-compose-up.sh --down

clean-all: clean-compose ## Clean up everything
	@echo "$(BLUE)Cleaning up everything...$(NC)"
	@docker system prune -f
	@echo "$(GREEN)Cleanup completed$(NC)"

# Testing
test: ## Run tests in Docker container
	@echo "$(BLUE)Running tests...$(NC)"
	@docker run --rm -v $(PWD):/app -w /app $(IMAGE_NAME):$(TAG) python -m pytest

test-coverage: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@docker run --rm -v $(PWD):/app -w /app $(IMAGE_NAME):$(TAG) python -m pytest --cov=backend --cov=frontend

# Development helpers
shell: ## Open shell in running container
	@echo "$(BLUE)Opening shell in container...$(NC)"
	@docker exec -it $(CONTAINER_NAME) /bin/bash

shell-compose: ## Open shell in Docker Compose container
	@echo "$(BLUE)Opening shell in Docker Compose container...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) exec contract-analyzer /bin/bash

# Database operations
db-init: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	@docker exec $(CONTAINER_NAME) python backend/app/scripts/seed_database.py

db-reset: ## Reset database
	@echo "$(BLUE)Resetting database...$(NC)"
	@docker exec $(CONTAINER_NAME) rm -f /app/data/contract_analyzer.db
	@make db-init

# Backup and restore
backup: ## Backup application data
	@echo "$(BLUE)Creating backup...$(NC)"
	@mkdir -p backups
	@docker run --rm -v $(PWD)/data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/contract-analyzer-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .

restore: ## Restore application data (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)Please specify BACKUP_FILE variable$(NC)"; \
		echo "Usage: make restore BACKUP_FILE=backups/contract-analyzer-20240101-120000.tar.gz"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring from $(BACKUP_FILE)...$(NC)"
	@docker run --rm -v $(PWD)/data:/data -v $(PWD)/backups:/backup alpine tar xzf /backup/$(BACKUP_FILE) -C /data

# Quick start commands
quick-start: build up-logs ## Quick start: build and run with logs
	@echo "$(GREEN)Quick start completed!$(NC)"
	@echo "$(BLUE)Backend API: http://localhost:8000$(NC)"
	@echo "$(BLUE)Frontend UI: http://localhost:8501$(NC)"

quick-stop: stop-compose ## Quick stop: stop all services
	@echo "$(GREEN)Quick stop completed!$(NC)"

# Show running containers
ps: ## Show running containers
	@echo "$(BLUE)Running containers:$(NC)"
	@docker ps --filter name=$(CONTAINER_NAME) --filter name=contract-analyzer

# Show Docker images
images: ## Show Docker images
	@echo "$(BLUE)Docker images:$(NC)"
	@docker images $(IMAGE_NAME)

# Show Docker volumes
volumes: ## Show Docker volumes
	@echo "$(BLUE)Docker volumes:$(NC)"
	@docker volume ls --filter name=contract-analyzer

# Show Docker networks
networks: ## Show Docker networks
	@echo "$(BLUE)Docker networks:$(NC)"
	@docker network ls --filter name=contract-analyzer