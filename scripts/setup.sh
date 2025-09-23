#!/bin/bash

# Contract Risk Analyzer Setup Script
# This script sets up the development environment and initializes the application

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to generate random string
generate_random_string() {
    openssl rand -hex 32
}

# Function to create directory if it doesn't exist
create_directory() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        print_status "Created directory: $1"
    fi
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.9"
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python $PYTHON_VERSION is installed"
            return 0
        else
            print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 is not installed"
        return 1
    fi
}

# Function to check if Poetry is installed
check_poetry() {
    if command_exists poetry; then
        POETRY_VERSION=$(poetry --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        print_success "Poetry $POETRY_VERSION is installed"
        return 0
    else
        print_warning "Poetry is not installed. Installing..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
        if command_exists poetry; then
            print_success "Poetry installed successfully"
            return 0
        else
            print_error "Failed to install Poetry"
            return 1
        fi
    fi
}

# Function to check if Docker is installed
check_docker() {
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        print_success "Docker $DOCKER_VERSION is installed"
        return 0
    else
        print_error "Docker is not installed. Please install Docker first."
        return 1
    fi
}

# Function to check if Docker Compose is installed
check_docker_compose() {
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        print_success "Docker Compose $COMPOSE_VERSION is installed"
        return 0
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        return 1
    fi
}

# Function to create environment file
create_env_file() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp config/env.template .env
        
        # Generate secure keys
        SECRET_KEY=$(generate_random_string)
        JWT_SECRET_KEY=$(generate_random_string)
        
        # Update .env file with generated keys
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your_32_character_secret_key_here/$SECRET_KEY/" .env
            sed -i '' "s/your_jwt_secret_key_here/$JWT_SECRET_KEY/" .env
        else
            # Linux
            sed -i "s/your_32_character_secret_key_here/$SECRET_KEY/" .env
            sed -i "s/your_jwt_secret_key_here/$JWT_SECRET_KEY/" .env
        fi
        
        print_success "Created .env file with generated keys"
        print_warning "Please update the API keys in .env file before running the application"
    else
        print_warning ".env file already exists"
    fi
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    poetry install
    print_success "Dependencies installed successfully"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    create_directory "data"
    create_directory "data/chroma"
    create_directory "data/uploads"
    create_directory "data/temp"
    create_directory "data/reports"
    create_directory "logs"
    create_directory "templates"
    create_directory "templates/reports"
    print_success "Directories created successfully"
}

# Function to check if required ports are available
check_ports() {
    print_status "Checking if required ports are available..."
    
    PORTS=(8000 8501 5432 6379 8001 9090 3000 9093 16686)
    PORTS_IN_USE=()
    
    for port in "${PORTS[@]}"; do
        if port_in_use $port; then
            PORTS_IN_USE+=($port)
        fi
    done
    
    if [ ${#PORTS_IN_USE[@]} -gt 0 ]; then
        print_warning "The following ports are already in use: ${PORTS_IN_USE[*]}"
        print_warning "You may need to stop the services using these ports or modify the configuration"
    else
        print_success "All required ports are available"
    fi
}

# Function to start Docker services
start_docker_services() {
    print_status "Starting Docker services..."
    docker-compose up -d postgres redis chroma
    print_success "Docker services started"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    until docker-compose exec postgres pg_isready -U user -d contract_analyzer; do
        sleep 2
    done
    print_success "PostgreSQL is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose exec redis redis-cli ping; do
        sleep 2
    done
    print_success "Redis is ready"
    
    # Wait for ChromaDB
    print_status "Waiting for ChromaDB..."
    until curl -s http://localhost:8001/api/v1/heartbeat >/dev/null 2>&1; do
        sleep 2
    done
    print_success "ChromaDB is ready"
}

# Function to create database tables
create_database_tables() {
    print_status "Creating database tables..."
    poetry run python contract_analyzer/backend/app/scripts/create_security_tables.py
    print_success "Database tables created successfully"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    poetry run pytest
    print_success "Tests completed successfully"
}

# Function to display setup summary
display_summary() {
    echo
    echo "=========================================="
    echo "  Contract Risk Analyzer Setup Complete"
    echo "=========================================="
    echo
    print_success "Setup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Update the API keys in .env file:"
    echo "   - OPENAI_API_KEY (required)"
    echo "   - ANTHROPIC_API_KEY (optional)"
    echo "   - Other integration keys as needed"
    echo
    echo "2. Start the application:"
    echo "   make up                    # Start all services with Docker"
    echo "   make run-backend          # Run backend only (development)"
    echo "   make run-frontend         # Run frontend only (development)"
    echo
    echo "3. Access the application:"
    echo "   - Frontend: http://localhost:8501"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo "   - Grafana: http://localhost:3000 (admin/admin123)"
    echo "   - Prometheus: http://localhost:9090"
    echo
    echo "4. Run tests:"
    echo "   make test"
    echo
    echo "5. View logs:"
    echo "   docker-compose logs -f"
    echo
    print_warning "Remember to update the API keys in .env before running the application!"
}

# Main setup function
main() {
    echo "=========================================="
    echo "  Contract Risk Analyzer Setup Script"
    echo "=========================================="
    echo
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python_version || exit 1
    check_poetry || exit 1
    check_docker || exit 1
    check_docker_compose || exit 1
    
    # Create environment file
    create_env_file
    
    # Install dependencies
    install_dependencies
    
    # Create directories
    create_directories
    
    # Check ports
    check_ports
    
    # Start Docker services
    start_docker_services
    
    # Wait for services
    wait_for_services
    
    # Create database tables
    create_database_tables
    
    # Run tests
    run_tests
    
    # Display summary
    display_summary
}

# Run main function
main "$@"
