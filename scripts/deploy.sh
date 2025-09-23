#!/bin/bash

# Contract Risk Analyzer Production Deployment Script
# This script deploys the application to production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to show help
show_help() {
    echo "Contract Risk Analyzer Production Deployment Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  build       Build Docker images"
    echo "  deploy      Deploy to production"
    echo "  rollback    Rollback to previous version"
    echo "  status      Show deployment status"
    echo "  logs        Show production logs"
    echo "  backup      Backup production data"
    echo "  restore     Restore from backup"
    echo "  health      Check application health"
    echo "  scale       Scale services"
    echo "  update      Update application"
    echo "  help        Show this help message"
    echo
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Please create it from config/env.template"
        exit 1
    fi
    
    # Check if required environment variables are set
    source .env
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
        print_error "OPENAI_API_KEY is not set in .env file"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your_32_character_secret_key_here" ]; then
        print_error "SECRET_KEY is not set in .env file"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    docker-compose build --no-cache
    print_success "Docker images built successfully"
}

# Function to deploy to production
deploy() {
    print_status "Deploying to production..."
    
    # Check prerequisites
    check_prerequisites
    
    # Build images
    build_images
    
    # Stop existing services
    print_status "Stopping existing services..."
    docker-compose down --remove-orphans
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check health
    health_check
    
    print_success "Deployment completed successfully"
}

# Function to rollback
rollback() {
    print_status "Rolling back to previous version..."
    
    # Get previous image tag
    PREVIOUS_TAG=$(docker images --format "table {{.Tag}}" | grep -v "latest" | head -n 1)
    
    if [ -z "$PREVIOUS_TAG" ]; then
        print_error "No previous version found"
        exit 1
    fi
    
    print_warning "Rolling back to version: $PREVIOUS_TAG"
    
    # Update docker-compose.yml to use previous tag
    sed -i "s/image: contract-analyzer:latest/image: contract-analyzer:$PREVIOUS_TAG/" docker-compose.yml
    
    # Restart services
    docker-compose down
    docker-compose up -d
    
    print_success "Rollback completed"
}

# Function to show deployment status
show_status() {
    print_status "Deployment status:"
    docker-compose ps
    echo
    print_status "Resource usage:"
    docker stats --no-stream
}

# Function to show logs
show_logs() {
    print_status "Showing production logs..."
    docker-compose logs -f
}

# Function to backup data
backup_data() {
    print_status "Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup PostgreSQL data
    print_status "Backing up PostgreSQL data..."
    docker-compose exec postgres pg_dump -U user contract_analyzer > "$BACKUP_DIR/postgres_backup.sql"
    
    # Backup Redis data
    print_status "Backing up Redis data..."
    docker-compose exec redis redis-cli --rdb "$BACKUP_DIR/redis_backup.rdb"
    
    # Backup ChromaDB data
    print_status "Backing up ChromaDB data..."
    docker cp $(docker-compose ps -q chroma):/chroma/data "$BACKUP_DIR/chroma_data"
    
    # Backup application data
    print_status "Backing up application data..."
    cp -r data "$BACKUP_DIR/"
    cp -r logs "$BACKUP_DIR/"
    
    # Create backup archive
    tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" .
    rm -rf "$BACKUP_DIR"
    
    print_success "Backup created: $BACKUP_DIR.tar.gz"
}

# Function to restore from backup
restore_backup() {
    if [ -z "$1" ]; then
        print_error "Please provide backup file path"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_status "Restoring from backup: $BACKUP_FILE"
    
    # Stop services
    docker-compose down
    
    # Extract backup
    BACKUP_DIR="restore_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    tar -xzf "$BACKUP_FILE" -C "$BACKUP_DIR"
    
    # Restore PostgreSQL data
    print_status "Restoring PostgreSQL data..."
    docker-compose up -d postgres
    sleep 10
    docker-compose exec postgres psql -U user -d contract_analyzer < "$BACKUP_DIR/postgres_backup.sql"
    
    # Restore Redis data
    print_status "Restoring Redis data..."
    docker-compose up -d redis
    sleep 5
    docker cp "$BACKUP_DIR/redis_backup.rdb" $(docker-compose ps -q redis):/data/dump.rdb
    docker-compose restart redis
    
    # Restore ChromaDB data
    print_status "Restoring ChromaDB data..."
    docker-compose up -d chroma
    sleep 5
    docker cp "$BACKUP_DIR/chroma_data" $(docker-compose ps -q chroma):/chroma/
    
    # Restore application data
    print_status "Restoring application data..."
    cp -r "$BACKUP_DIR/data" ./
    cp -r "$BACKUP_DIR/logs" ./
    
    # Clean up
    rm -rf "$BACKUP_DIR"
    
    # Start all services
    docker-compose up -d
    
    print_success "Restore completed"
}

# Function to check application health
health_check() {
    print_status "Checking application health..."
    
    # Check backend health
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend is not responding"
        return 1
    fi
    
    # Check frontend health
    if curl -s http://localhost:8501 >/dev/null 2>&1; then
        print_success "Frontend is healthy"
    else
        print_error "Frontend is not responding"
        return 1
    fi
    
    # Check database health
    if docker-compose exec postgres pg_isready -U user -d contract_analyzer >/dev/null 2>&1; then
        print_success "PostgreSQL is healthy"
    else
        print_error "PostgreSQL is not responding"
        return 1
    fi
    
    # Check Redis health
    if docker-compose exec redis redis-cli ping >/dev/null 2>&1; then
        print_success "Redis is healthy"
    else
        print_error "Redis is not responding"
        return 1
    fi
    
    # Check ChromaDB health
    if curl -s http://localhost:8001/api/v1/heartbeat >/dev/null 2>&1; then
        print_success "ChromaDB is healthy"
    else
        print_error "ChromaDB is not responding"
        return 1
    fi
    
    print_success "All services are healthy"
}

# Function to scale services
scale_services() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        print_error "Usage: $0 scale <service> <replicas>"
        exit 1
    fi
    
    SERVICE="$1"
    REPLICAS="$2"
    
    print_status "Scaling $SERVICE to $REPLICAS replicas..."
    docker-compose up -d --scale "$SERVICE=$REPLICAS"
    print_success "Scaling completed"
}

# Function to update application
update_application() {
    print_status "Updating application..."
    
    # Pull latest changes
    git pull origin main
    
    # Build new images
    build_images
    
    # Deploy
    deploy
    
    print_success "Application updated"
}

# Main function
main() {
    case "${1:-help}" in
        build)
            build_images
            ;;
        deploy)
            deploy
            ;;
        rollback)
            rollback
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_backup "$2"
            ;;
        health)
            health_check
            ;;
        scale)
            scale_services "$2" "$3"
            ;;
        update)
            update_application
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
