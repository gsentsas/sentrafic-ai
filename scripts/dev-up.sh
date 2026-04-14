#!/bin/bash

# SEN TRAFIC AI - Development Environment Setup Script
# Starts Docker Compose services and initializes the environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/.env"
MAX_RETRIES=30
RETRY_DELAY=2

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_info() {
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

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker installation
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed: $(docker --version)"

    # Check Docker Compose installation
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed: $(docker-compose --version)"

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    print_success "Docker daemon is running"

    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env file not found"
        print_info "Creating .env from .env.example..."
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
            print_success ".env file created"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_success ".env file found"
    fi
}

start_services() {
    print_header "Starting Docker Compose Services"

    cd "$PROJECT_ROOT"

    # Build images
    print_info "Building Docker images..."
    docker-compose build --progress=plain

    # Start services
    print_info "Starting services..."
    docker-compose up -d

    print_success "Services started"
}

wait_for_postgres() {
    print_header "Waiting for PostgreSQL"

    local retry_count=0
    local postgres_ready=false

    while [ $retry_count -lt $MAX_RETRIES ]; do
        if docker-compose exec -T postgres pg_isready -U sentrafic &> /dev/null; then
            postgres_ready=true
            break
        fi

        retry_count=$((retry_count + 1))
        print_info "PostgreSQL not ready yet (attempt $retry_count/$MAX_RETRIES)"
        sleep $RETRY_DELAY
    done

    if [ "$postgres_ready" = false ]; then
        print_error "PostgreSQL failed to start after $MAX_RETRIES attempts"
        print_error "Check logs with: docker-compose logs postgres"
        exit 1
    fi

    print_success "PostgreSQL is ready"
}

wait_for_redis() {
    print_header "Waiting for Redis"

    local retry_count=0
    local redis_ready=false

    while [ $retry_count -lt $MAX_RETRIES ]; do
        if docker-compose exec -T redis redis-cli ping &> /dev/null; then
            redis_ready=true
            break
        fi

        retry_count=$((retry_count + 1))
        print_info "Redis not ready yet (attempt $retry_count/$MAX_RETRIES)"
        sleep $RETRY_DELAY
    done

    if [ "$redis_ready" = false ]; then
        print_error "Redis failed to start after $MAX_RETRIES attempts"
        print_error "Check logs with: docker-compose logs redis"
        exit 1
    fi

    print_success "Redis is ready"
}

wait_for_backend() {
    print_header "Waiting for Backend API"

    local retry_count=0
    local backend_ready=false

    while [ $retry_count -lt $MAX_RETRIES ]; do
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            backend_ready=true
            break
        fi

        retry_count=$((retry_count + 1))
        print_info "Backend API not ready yet (attempt $retry_count/$MAX_RETRIES)"
        sleep $RETRY_DELAY
    done

    if [ "$backend_ready" = false ]; then
        print_error "Backend API failed to start after $MAX_RETRIES attempts"
        print_error "Check logs with: docker-compose logs backend-api"
        exit 1
    fi

    print_success "Backend API is ready"
}

check_service_status() {
    print_header "Service Status"

    docker-compose ps
}

print_summary() {
    print_header "Development Environment Ready"

    echo -e ""
    echo -e "${GREEN}All services are running!${NC}"
    echo -e ""
    echo -e "Service URLs:"
    echo -e "  ${BLUE}Dashboard${NC}:        ${GREEN}http://localhost:3001${NC}"
    echo -e "  ${BLUE}Backend API${NC}:       ${GREEN}http://localhost:8000${NC}"
    echo -e "  ${BLUE}API Docs${NC}:          ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  ${BLUE}PostgreSQL${NC}:        ${GREEN}localhost:5432${NC}"
    echo -e "  ${BLUE}Redis${NC}:             ${GREEN}localhost:6379${NC}"
    echo -e ""
    echo -e "Useful commands:"
    echo -e "  ${YELLOW}View logs${NC}:         docker-compose logs -f [service-name]"
    echo -e "  ${YELLOW}Stop services${NC}:     ./scripts/dev-down.sh"
    echo -e "  ${YELLOW}Seed data${NC}:         ./scripts/seed-demo.sh"
    echo -e "  ${YELLOW}Run vision${NC}:        ./scripts/run-vision-demo.sh"
    echo -e ""
}

main() {
    print_header "SEN TRAFIC AI - Development Environment Setup"

    check_prerequisites
    start_services
    wait_for_postgres
    wait_for_redis
    wait_for_backend
    check_service_status
    print_summary
}

# Run main function
main
