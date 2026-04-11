#!/bin/bash

# SEN TRAFIC AI - Development Environment Cleanup Script
# Stops Docker Compose services and optionally removes volumes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOVE_VOLUMES=false

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

show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -v, --volumes    Remove volumes (WARNING: deletes all data)"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Stop services, keep data"
    echo "  $0 --volumes        # Stop services and delete volumes"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--volumes)
                REMOVE_VOLUMES=true
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
}

stop_services() {
    print_header "Stopping Docker Compose Services"

    cd "$PROJECT_ROOT"

    # Check if docker-compose is running
    if ! docker-compose ps | grep -q "Up"; then
        print_warning "No running services found"
        return 0
    fi

    # Stop services
    print_info "Stopping services..."
    docker-compose down

    print_success "Services stopped"
}

remove_volumes() {
    print_header "Removing Data Volumes"

    print_warning "This will delete all data in the volumes!"
    echo -n "Are you sure? (yes/no): "
    read -r confirmation

    if [ "$confirmation" != "yes" ]; then
        print_info "Aborted. Data preserved."
        return 0
    fi

    cd "$PROJECT_ROOT"

    print_info "Removing volumes..."
    docker-compose down -v

    print_success "Volumes removed"
}

clean_images() {
    print_header "Cleaning Up Images (Optional)"

    echo -n "Remove Docker images? (yes/no): "
    read -r confirmation

    if [ "$confirmation" != "yes" ]; then
        print_info "Skipping image cleanup"
        return 0
    fi

    cd "$PROJECT_ROOT"

    print_info "Removing images..."
    docker-compose down --rmi all

    print_success "Images removed"
}

print_summary() {
    print_header "Cleanup Complete"

    if [ "$REMOVE_VOLUMES" = true ]; then
        echo -e "${GREEN}Services stopped and volumes removed${NC}"
    else
        echo -e "${GREEN}Services stopped (data preserved)${NC}"
    fi

    echo ""
    echo "To restart services, run:"
    echo -e "  ${YELLOW}./scripts/dev-up.sh${NC}"
    echo ""
}

main() {
    print_header "SEN TRAFIC AI - Development Environment Cleanup"

    parse_arguments "$@"

    stop_services

    if [ "$REMOVE_VOLUMES" = true ]; then
        remove_volumes
    fi

    print_summary
}

# Run main function
main "$@"
