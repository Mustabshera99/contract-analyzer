#!/bin/bash

# Contract Risk Analyzer - Docker Run Script
# This script runs the Contract Risk Analyzer application using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="contract-analyzer"
TAG="latest"
CONTAINER_NAME="contract-analyzer-app"
BACKEND_PORT=8000
FRONTEND_PORT=8501
REDIS_PORT=6379

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -i, --image IMAGE     Docker image name (default: contract-analyzer)"
    echo "  -t, --tag TAG         Docker image tag (default: latest)"
    echo "  -n, --name NAME       Container name (default: contract-analyzer-app)"
    echo "  -b, --backend-port    Backend port (default: 8000)"
    echo "  -f, --frontend-port   Frontend port (default: 8501)"
    echo "  -r, --redis-port      Redis port (default: 6379)"
    echo "  -d, --detach          Run in detached mode"
    echo "  --rm                  Remove container when it exits"
    echo "  --env-file FILE       Environment file (default: .env)"
    echo "  --no-redis            Don't start Redis container"
    echo "  --logs                Show logs after starting"
    echo "  --stop                Stop running containers"
    echo "  --clean               Stop and remove containers and volumes"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run with default settings"
    echo "  $0 -d --logs                         # Run in detached mode and show logs"
    echo "  $0 --stop                            # Stop running containers"
    echo "  $0 --clean                           # Clean up everything"
}

# Parse command line arguments
DETACH=false
REMOVE=false
ENV_FILE=".env"
NO_REDIS=false
SHOW_LOGS=false
STOP_CONTAINERS=false
CLEAN_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -b|--backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        -f|--frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        -r|--redis-port)
            REDIS_PORT="$2"
            shift 2
            ;;
        -d|--detach)
            DETACH=true
            shift
            ;;
        --rm)
            REMOVE=true
            shift
            ;;
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        --no-redis)
            NO_REDIS=true
            shift
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        --stop)
            STOP_CONTAINERS=true
            shift
            ;;
        --clean)
            CLEAN_ALL=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to stop containers
stop_containers() {
    print_status "Stopping Contract Analyzer containers..."
    
    # Stop main container
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker stop "$CONTAINER_NAME"
        print_success "Stopped container: $CONTAINER_NAME"
    fi
    
    # Stop Redis container
    if docker ps -q -f name="contract-analyzer-redis" | grep -q .; then
        docker stop contract-analyzer-redis
        print_success "Stopped Redis container"
    fi
    
    # Stop Nginx container
    if docker ps -q -f name="contract-analyzer-nginx" | grep -q .; then
        docker stop contract-analyzer-nginx
        print_success "Stopped Nginx container"
    fi
}

# Function to clean up everything
clean_all() {
    print_status "Cleaning up Contract Analyzer resources..."
    
    # Stop containers
    stop_containers
    
    # Remove containers
    if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        docker rm "$CONTAINER_NAME"
        print_success "Removed container: $CONTAINER_NAME"
    fi
    
    if docker ps -aq -f name="contract-analyzer-redis" | grep -q .; then
        docker rm contract-analyzer-redis
        print_success "Removed Redis container"
    fi
    
    if docker ps -aq -f name="contract-analyzer-nginx" | grep -q .; then
        docker rm contract-analyzer-nginx
        print_success "Removed Nginx container"
    fi
    
    # Remove volumes
    if docker volume ls -q -f name="contract-analyzer" | grep -q .; then
        docker volume rm $(docker volume ls -q -f name="contract-analyzer")
        print_success "Removed volumes"
    fi
    
    # Remove network
    if docker network ls -q -f name="contract-analyzer" | grep -q .; then
        docker network rm contract-analyzer-network 2>/dev/null || true
        print_success "Removed network"
    fi
}

# Handle stop and clean operations
if [[ "$STOP_CONTAINERS" == true ]]; then
    stop_containers
    exit 0
fi

if [[ "$CLEAN_ALL" == true ]]; then
    clean_all
    exit 0
fi

# Check if image exists
FULL_IMAGE_NAME="$IMAGE_NAME:$TAG"
if ! docker images "$FULL_IMAGE_NAME" | grep -q "$IMAGE_NAME"; then
    print_error "Docker image not found: $FULL_IMAGE_NAME"
    print_status "Please build the image first using: ./scripts/docker-build.sh"
    exit 1
fi

# Check if .env file exists
if [[ ! -f "$ENV_FILE" ]]; then
    print_warning "Environment file not found: $ENV_FILE"
    if [[ -f "env.template" ]]; then
        print_status "Creating .env from template..."
        cp env.template .env
        print_warning "Please update the .env file with your configuration before running the application."
    else
        print_error "env.template file not found. Please create a .env file manually."
        exit 1
    fi
fi

# Stop existing containers if they're running
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    print_warning "Container $CONTAINER_NAME is already running. Stopping it first..."
    docker stop "$CONTAINER_NAME"
fi

# Create necessary directories
mkdir -p logs/backend logs/frontend logs/audit logs/nginx

# Prepare Docker run command
DOCKER_CMD="docker run"
if [[ "$DETACH" == true ]]; then
    DOCKER_CMD="$DOCKER_CMD -d"
fi

if [[ "$REMOVE" == true ]]; then
    DOCKER_CMD="$DOCKER_CMD --rm"
fi

# Add container name
DOCKER_CMD="$DOCKER_CMD --name $CONTAINER_NAME"

# Add ports
DOCKER_CMD="$DOCKER_CMD -p $BACKEND_PORT:8000 -p $FRONTEND_PORT:8501"

# Add environment file
DOCKER_CMD="$DOCKER_CMD --env-file $ENV_FILE"

# Add volumes
DOCKER_CMD="$DOCKER_CMD -v $(pwd)/logs:/app/logs"
DOCKER_CMD="$DOCKER_CMD -v $(pwd)/data:/app/data"

# Add image
DOCKER_CMD="$DOCKER_CMD $FULL_IMAGE_NAME"

# Start Redis if not disabled
if [[ "$NO_REDIS" == false ]]; then
    print_status "Starting Redis container..."
    if ! docker ps -q -f name="contract-analyzer-redis" | grep -q .; then
        docker run -d \
            --name contract-analyzer-redis \
            -p $REDIS_PORT:6379 \
            -v contract-analyzer-redis-data:/data \
            redis:7-alpine \
            redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
        print_success "Redis container started"
    else
        print_warning "Redis container is already running"
    fi
fi

# Start the main application
print_status "Starting Contract Analyzer application..."
print_status "Command: $DOCKER_CMD"

if eval $DOCKER_CMD; then
    print_success "Contract Analyzer application started successfully!"
    print_status "Backend API: http://localhost:$BACKEND_PORT"
    print_status "Frontend UI: http://localhost:$FRONTEND_PORT"
    print_status "API Documentation: http://localhost:$BACKEND_PORT/docs"
    
    if [[ "$DETACH" == true ]]; then
        print_status "Container is running in detached mode"
        print_status "To view logs: docker logs $CONTAINER_NAME"
        print_status "To stop: docker stop $CONTAINER_NAME"
        
        if [[ "$SHOW_LOGS" == true ]]; then
            print_status "Showing logs..."
            docker logs -f "$CONTAINER_NAME"
        fi
    else
        print_status "Press Ctrl+C to stop the application"
    fi
else
    print_error "Failed to start Contract Analyzer application"
    exit 1
fi
