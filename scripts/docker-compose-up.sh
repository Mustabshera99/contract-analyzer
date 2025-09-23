#!/bin/bash

# Contract Risk Analyzer - Docker Compose Up Script
# This script starts the Contract Risk Analyzer application using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

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
    echo "  -f, --file FILE       Docker Compose file (default: docker-compose.yml)"
    echo "  -e, --env-file FILE   Environment file (default: .env)"
    echo "  -d, --detach          Run in detached mode"
    echo "  --build               Build images before starting"
    echo "  --no-build            Don't build images (use existing)"
    echo "  --force-recreate      Recreate containers even if config hasn't changed"
    echo "  --remove-orphans      Remove containers for services not defined in compose file"
    echo "  --scale SERVICE=NUM   Scale a service to NUM instances"
    echo "  --logs                Show logs after starting"
    echo "  --follow              Follow log output"
    echo "  --stop                Stop all services"
    echo "  --down                Stop and remove containers, networks, and volumes"
    echo "  --restart             Restart all services"
    echo "  --status              Show status of services"
    echo "  --health              Show health status of services"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Start with default settings"
    echo "  $0 -d --build --logs                 # Start in detached mode, build, and show logs"
    echo "  $0 --stop                            # Stop all services"
    echo "  $0 --down                            # Stop and remove everything"
    echo "  $0 --restart                         # Restart all services"
    echo "  $0 --status                          # Show service status"
}

# Parse command line arguments
DETACH=false
BUILD_IMAGES=true
FORCE_RECREATE=false
REMOVE_ORPHANS=false
SCALE_SERVICES=""
SHOW_LOGS=false
FOLLOW_LOGS=false
STOP_SERVICES=false
DOWN_SERVICES=false
RESTART_SERVICES=false
SHOW_STATUS=false
SHOW_HEALTH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -e|--env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        -d|--detach)
            DETACH=true
            shift
            ;;
        --build)
            BUILD_IMAGES=true
            shift
            ;;
        --no-build)
            BUILD_IMAGES=false
            shift
            ;;
        --force-recreate)
            FORCE_RECREATE=true
            shift
            ;;
        --remove-orphans)
            REMOVE_ORPHANS=true
            shift
            ;;
        --scale)
            SCALE_SERVICES="$2"
            shift 2
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        --follow)
            FOLLOW_LOGS=true
            shift
            ;;
        --stop)
            STOP_SERVICES=true
            shift
            ;;
        --down)
            DOWN_SERVICES=true
            shift
            ;;
        --restart)
            RESTART_SERVICES=true
            shift
            ;;
        --status)
            SHOW_STATUS=true
            shift
            ;;
        --health)
            SHOW_HEALTH=true
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

# Validate compose file
if [[ ! -f "$COMPOSE_FILE" ]]; then
    print_error "Docker Compose file not found: $COMPOSE_FILE"
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

# Function to stop services
stop_services() {
    print_status "Stopping Contract Analyzer services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" stop
    print_success "Services stopped"
}

# Function to bring down services
down_services() {
    print_status "Stopping and removing Contract Analyzer services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    print_success "Services stopped and removed"
}

# Function to restart services
restart_services() {
    print_status "Restarting Contract Analyzer services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart
    print_success "Services restarted"
}

# Function to show status
show_status() {
    print_status "Contract Analyzer services status:"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
}

# Function to show health
show_health() {
    print_status "Contract Analyzer services health:"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    # Check individual service health
    print_status "Checking service health..."
    
    # Check backend health
    if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps contract-analyzer | grep -q "Up"; then
        if curl -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
            print_success "Backend API is healthy"
        else
            print_warning "Backend API is running but not responding to health checks"
        fi
    else
        print_error "Backend API is not running"
    fi
    
    # Check frontend health
    if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps contract-analyzer | grep -q "Up"; then
        if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
            print_success "Frontend is healthy"
        else
            print_warning "Frontend is running but not responding to health checks"
        fi
    else
        print_error "Frontend is not running"
    fi
    
    # Check Redis health
    if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps redis | grep -q "Up"; then
        if docker exec contract-analyzer-redis redis-cli ping >/dev/null 2>&1; then
            print_success "Redis is healthy"
        else
            print_warning "Redis is running but not responding to ping"
        fi
    else
        print_error "Redis is not running"
    fi
}

# Handle special operations
if [[ "$STOP_SERVICES" == true ]]; then
    stop_services
    exit 0
fi

if [[ "$DOWN_SERVICES" == true ]]; then
    down_services
    exit 0
fi

if [[ "$RESTART_SERVICES" == true ]]; then
    restart_services
    exit 0
fi

if [[ "$SHOW_STATUS" == true ]]; then
    show_status
    exit 0
fi

if [[ "$SHOW_HEALTH" == true ]]; then
    show_health
    exit 0
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs/backend logs/frontend logs/audit logs/nginx data/chroma data/temp security

# Prepare docker-compose command
COMPOSE_CMD="docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE"

# Add build option
if [[ "$BUILD_IMAGES" == true ]]; then
    COMPOSE_CMD="$COMPOSE_CMD --build"
fi

# Add detach option
if [[ "$DETACH" == true ]]; then
    COMPOSE_CMD="$COMPOSE_CMD -d"
fi

# Add force recreate option
if [[ "$FORCE_RECREATE" == true ]]; then
    COMPOSE_CMD="$COMPOSE_CMD --force-recreate"
fi

# Add remove orphans option
if [[ "$REMOVE_ORPHANS" == true ]]; then
    COMPOSE_CMD="$COMPOSE_CMD --remove-orphans"
fi

# Add scale option
if [[ -n "$SCALE_SERVICES" ]]; then
    COMPOSE_CMD="$COMPOSE_CMD --scale $SCALE_SERVICES"
fi

# Add up command
COMPOSE_CMD="$COMPOSE_CMD up"

# Start services
print_status "Starting Contract Analyzer services..."
print_status "Command: $COMPOSE_CMD"

if eval $COMPOSE_CMD; then
    print_success "Contract Analyzer services started successfully!"
    print_status "Backend API: http://localhost:8000"
    print_status "Frontend UI: http://localhost:8501"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Redis: localhost:6379"
    
    if [[ "$DETACH" == true ]]; then
        print_status "Services are running in detached mode"
        print_status "To view logs: docker-compose logs -f"
        print_status "To stop: docker-compose down"
        
        if [[ "$SHOW_LOGS" == true ]]; then
            print_status "Showing logs..."
            if [[ "$FOLLOW_LOGS" == true ]]; then
                docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f
            else
                docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs
            fi
        fi
    else
        print_status "Press Ctrl+C to stop the services"
    fi
else
    print_error "Failed to start Contract Analyzer services"
    exit 1
fi
