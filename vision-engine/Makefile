.PHONY: help install test run clean lint format download-model demo

help:
	@echo "SEN TRAFIC AI Vision Engine - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install all dependencies"
	@echo "  make download-model   Download YOLOv8 nano model"
	@echo ""
	@echo "Running:"
	@echo "  make run              Run vision engine with demo"
	@echo "  make demo             Run with visualization enabled"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make lint             Run code style checks"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            Remove generated files"
	@echo "  make format           Format code with black"
	@echo ""
	@echo "Configuration:"
	@echo "  make setup-env        Copy .env.example to .env"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

download-model:
	@echo "Downloading YOLOv8 nano model..."
	python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
	@echo "Model downloaded successfully!"

setup-env:
	@if [ -f .env ]; then \
		echo ".env already exists"; \
	else \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo ".env created. Update with your settings."; \
	fi

test:
	@echo "Running test suite..."
	pytest tests/ -q

test-verbose:
	@echo "Running tests with verbose output..."
	pytest tests/ -v

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

run: setup-env download-model
	@echo "Starting vision engine..."
	python -m app.main

demo: setup-env download-model
	@echo "Starting vision engine in demo mode..."
	DISPLAY_OUTPUT=true python -m app.main

lint:
	@echo "Checking code style..."
	python -m py_compile app/*.py tests/*.py
	@echo "All Python files compile successfully!"

format:
	@echo "Formatting code..."
	find app tests -name "*.py" -type f | xargs python -m black

clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -delete
	rm -f .coverage
	@echo "Cleanup complete!"

.DEFAULT_GOAL := help
