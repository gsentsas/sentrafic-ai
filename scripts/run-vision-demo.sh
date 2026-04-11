#!/bin/bash

# SEN TRAFIC AI - Vision Engine Demo Script
# Runs the vision engine locally against a demo video file

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VISION_ENGINE_DIR="$PROJECT_ROOT/vision-engine"
DEMO_VIDEO="$PROJECT_ROOT/samples/videos/demo.mp4"
PYTHON_VENV="$VISION_ENGINE_DIR/venv"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
RUN_MODE="${1:-demo}"  # demo or local

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
    echo "  demo       Run vision engine against demo video (default)"
    echo "  local      Run vision engine with local setup"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                   # Run with demo video"
    echo "  $0 demo              # Run with demo video (explicit)"
    echo "  $0 local             # Run with local Python setup"
}

check_vision_engine() {
    print_header "Checking Vision Engine Setup"

    if [ ! -d "$VISION_ENGINE_DIR" ]; then
        print_error "Vision engine directory not found: $VISION_ENGINE_DIR"
        exit 1
    fi
    print_success "Vision engine directory found"

    if [ ! -f "$VISION_ENGINE_DIR/main.py" ]; then
        print_error "main.py not found in vision engine directory"
        exit 1
    fi
    print_success "Vision engine code found"

    if [ ! -f "$VISION_ENGINE_DIR/requirements.txt" ]; then
        print_error "requirements.txt not found in vision engine directory"
        exit 1
    fi
    print_success "Vision engine dependencies found"
}

check_demo_video() {
    print_header "Checking Demo Video"

    if [ ! -f "$DEMO_VIDEO" ]; then
        print_warning "Demo video not found at: $DEMO_VIDEO"
        print_info "Creating samples directory..."
        mkdir -p "$(dirname "$DEMO_VIDEO")"

        print_info ""
        print_info "You need to provide a video file at: $DEMO_VIDEO"
        print_info "You can:"
        print_info "  1. Download a traffic video"
        print_info "  2. Record your own using a camera"
        print_info "  3. Create a test video with: ffmpeg -f lavfi -i testsrc=size=1280x720:duration=30 -y $DEMO_VIDEO"
        print_info ""
        exit 1
    fi
    print_success "Demo video found: $DEMO_VIDEO"
}

check_backend() {
    print_header "Checking Backend API"

    print_info "Checking backend at $BACKEND_URL..."

    for i in {1..5}; do
        if curl -s "$BACKEND_URL/api/health" > /dev/null 2>&1; then
            print_success "Backend is available"
            return 0
        fi
        print_info "Attempt $i/5 - Waiting for backend..."
        sleep 2
    done

    print_warning "Backend is not responding at $BACKEND_URL"
    print_warning "Vision engine will still run but won't publish events"
}

setup_local_environment() {
    print_header "Setting Up Local Python Environment"

    cd "$VISION_ENGINE_DIR"

    # Check if virtual environment exists
    if [ ! -d "$PYTHON_VENV" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"

    # Install dependencies
    print_info "Installing dependencies (this may take a while)..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

    print_success "Dependencies installed"
}

run_vision_engine_docker() {
    print_header "Running Vision Engine in Docker"

    cd "$PROJECT_ROOT"

    print_info "Building vision engine Docker image..."
    docker-compose build vision-engine

    print_info "Starting vision engine..."
    docker-compose up vision-engine

    print_success "Vision engine stopped"
}

run_vision_engine_local() {
    print_header "Running Vision Engine Locally"

    cd "$VISION_ENGINE_DIR"

    # Source virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi

    # Set environment variables
    export VISION_SOURCE="$DEMO_VIDEO"
    export VISION_BACKEND_URL="$BACKEND_URL"
    export VISION_CAMERA_ID="demo-camera-1"
    export VISION_CAMERA_NAME="Demo Camera"
    export YOLO_MODEL="yolov8n.pt"
    export YOLO_CONFIDENCE="0.5"
    export VISION_FPS="30"
    export VISION_FRAME_WIDTH="1280"
    export VISION_FRAME_HEIGHT="720"
    export LOG_LEVEL="INFO"

    print_info "Starting vision engine with configuration:"
    print_info "  Video Source: $VISION_SOURCE"
    print_info "  Backend URL: $VISION_BACKEND_URL"
    print_info "  Camera ID: $VISION_CAMERA_ID"
    print_info "  YOLO Model: $YOLO_MODEL"
    print_info ""
    print_info "Press Ctrl+C to stop..."
    print_info ""

    # Run vision engine
    python main.py

    print_success "Vision engine stopped"
}

print_summary() {
    print_header "Vision Engine Demo Complete"

    echo -e ""
    echo -e "${GREEN}Vision engine demo has completed!${NC}"
    echo -e ""
    echo -e "Next steps:"
    echo -e "  1. Check the dashboard at ${YELLOW}http://localhost:3000${NC}"
    echo -e "  2. View analytics at ${YELLOW}http://localhost:8000/api/analytics/traffic${NC}"
    echo -e "  3. Check API docs at ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e ""
}

main() {
    print_header "SEN TRAFIC AI - Vision Engine Demo"

    # Parse arguments
    case "$RUN_MODE" in
        demo|--demo|-d)
            print_info "Running in DOCKER mode with demo video"
            check_vision_engine
            check_demo_video
            check_backend
            run_vision_engine_docker
            ;;
        local|--local|-l)
            print_info "Running in LOCAL mode with demo video"
            check_vision_engine
            check_demo_video
            setup_local_environment
            run_vision_engine_local
            ;;
        help|--help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown mode: $RUN_MODE"
            show_usage
            exit 1
            ;;
    esac

    print_summary
}

# Run main function
main
