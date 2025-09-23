#!/bin/bash

# Contract Risk Analyzer - Docker Build Script
# This script builds the Docker image for the Contract Risk Analyzer application

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
DOCKERFILE="Dockerfile"
BUILD_CONTEXT="."

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
    echo "  -t, --tag TAG        Docker image tag (default: latest)"
    echo "  -n, --name NAME      Docker image name (default: contract-analyzer)"
    echo "  -f, --file FILE      Dockerfile path (default: Dockerfile)"
    echo "  -c, --context PATH   Build context path (default: .)"
    echo "  --no-cache          Build without using cache"
    echo "  --push              Push image to registry after building"
    echo "  --registry REGISTRY Registry URL for pushing (default: docker.io)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build with default settings"
    echo "  $0 -t v1.0.0                        # Build with specific tag"
    echo "  $0 --no-cache --push                # Build without cache and push"
    echo "  $0 --registry myregistry.com        # Push to custom registry"
}

# Parse command line arguments
PUSH_IMAGE=false
NO_CACHE=false
REGISTRY="docker.io"

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -f|--file)
            DOCKERFILE="$2"
            shift 2
            ;;
        -c|--context)
            BUILD_CONTEXT="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
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

# Validate inputs
if [[ ! -f "$DOCKERFILE" ]]; then
    print_error "Dockerfile not found: $DOCKERFILE"
    exit 1
fi

if [[ ! -d "$BUILD_CONTEXT" ]]; then
    print_error "Build context directory not found: $BUILD_CONTEXT"
    exit 1
fi

# Set full image name
FULL_IMAGE_NAME="$IMAGE_NAME:$TAG"
if [[ "$REGISTRY" != "docker.io" ]]; then
    FULL_IMAGE_NAME="$REGISTRY/$FULL_IMAGE_NAME"
fi

print_status "Building Docker image: $FULL_IMAGE_NAME"
print_status "Dockerfile: $DOCKERFILE"
print_status "Build context: $BUILD_CONTEXT"

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    print_warning ".env file not found. Creating from template..."
    if [[ -f "env.template" ]]; then
        cp env.template .env
        print_warning "Please update the .env file with your configuration before running the application."
    else
        print_error "env.template file not found. Please create a .env file manually."
        exit 1
    fi
fi

# Build the Docker image
BUILD_ARGS=""
if [[ "$NO_CACHE" == true ]]; then
    BUILD_ARGS="$BUILD_ARGS --no-cache"
fi

print_status "Starting Docker build..."
if docker build $BUILD_ARGS -f "$DOCKERFILE" -t "$FULL_IMAGE_NAME" "$BUILD_CONTEXT"; then
    print_success "Docker image built successfully: $FULL_IMAGE_NAME"
else
    print_error "Docker build failed"
    exit 1
fi

# Show image information
print_status "Image information:"
docker images "$FULL_IMAGE_NAME"

# Push image if requested
if [[ "$PUSH_IMAGE" == true ]]; then
    print_status "Pushing image to registry..."
    if docker push "$FULL_IMAGE_NAME"; then
        print_success "Image pushed successfully: $FULL_IMAGE_NAME"
    else
        print_error "Failed to push image"
        exit 1
    fi
fi

print_success "Build completed successfully!"
print_status "To run the application:"
print_status "  docker run -p 8000:8000 -p 8501:8501 $FULL_IMAGE_NAME"
print_status "Or use docker-compose:"
print_status "  docker-compose up -d"
