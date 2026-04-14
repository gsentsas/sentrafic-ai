# SEN TRAFIC AI - Senegal Traffic Analysis Platform

A comprehensive computer vision traffic analysis platform for Senegal, built with modern cloud-native technologies. Real-time vehicle detection, tracking, and traffic analytics powered by YOLO object detection and ByteTrack multi-object tracking.

## Overview

SEN TRAFIC AI is designed to provide intelligent traffic monitoring and analysis for Dakar and other Senegalese cities. The platform processes video feeds from fixed traffic cameras, detects and tracks vehicles in real-time, and aggregates traffic metrics for operational insights and urban planning.

## Key Features

- **Real-time Vehicle Detection**: YOLO-based object detection for accurate vehicle identification
- **Multi-Object Tracking**: ByteTrack algorithm for persistent vehicle tracking across frames
- **Traffic Metrics**: Lane crossing counts, zone occupancy, vehicle classification
- **Web Dashboard**: Intuitive Next.js interface with real-time traffic analytics
- **RESTful API**: Complete API for integration with external systems
- **Scalable Architecture**: Containerized services with PostgreSQL and Redis
- **Health Monitoring**: Built-in camera health checks and system monitoring

## System Architecture

SEN TRAFIC AI is organized as a monorepo with four main parts:

### Services

1. **backend-api** - FastAPI application providing REST endpoints, database management, and real-time event aggregation
2. **vision-engine** - Python service running YOLO detection and tracking, processes video streams and publishes metrics
3. **dashboard** - Next.js React application providing the user interface for traffic analysis and monitoring
4. **infra (logical)** - infrastructure concerns handled by root `docker-compose.yml` and deployment docs

### Architecture Diagram

```
Camera Streams
     ↓
Vision Engine (YOLO + ByteTrack)
     ↓
Backend API (FastAPI + PostgreSQL + Redis)
     ↓
Dashboard (Next.js)
     ↓
Users / External Systems
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 14
- **Cache**: Redis 6+
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **API Documentation**: OpenAPI/Swagger

### Vision Engine
- **Detection**: YOLOv8 (ultralytics)
- **Tracking**: ByteTrack
- **Video Processing**: OpenCV
- **Inference**: CUDA-enabled GPU support

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks / Context API
- **Charts**: Recharts

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Docker Compose (development), Kubernetes-ready (production)
- **Reverse Proxy**: Nginx (production)
- **Monitoring**: Built-in health checks

## Quick Start

### Prerequisites

- Docker and Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- NVIDIA GPU (optional, for faster inference)
- For manual setup: Python 3.10+, Node.js 18+, PostgreSQL 14, Redis 6

### Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/senegal-ai/sen-trafic-ai.git
cd sen-trafic-ai

# Copy example environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend-api
```

Services will be available at:
- Dashboard: http://localhost:3001
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Postgres: localhost:5432
- Redis: localhost:6379

### Manual Setup

#### Backend API

```bash
cd backend-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create database
createdb sentrafic

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Vision Engine

```bash
cd vision-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download YOLO model
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Start vision engine
python -m app.main
```

#### Dashboard

```bash
cd dashboard

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Start development server
npm run dev
```

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Database
POSTGRES_USER=sentrafic
POSTGRES_PASSWORD=sentrafic_dev
POSTGRES_DB=sentrafic
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Cache
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET=your-secret-key-change-in-production

# API
BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Vision Engine
YOLO_MODEL=yolov8n.pt
VISION_SOURCE=samples/videos/demo.mp4
VISION_DEMO_MODE=true
```

## API Endpoints Summary

### Authentication
- `POST /api/auth/login` - User login

### System
- `GET /api/health` - Health check

### Dashboard
- `GET /api/dashboard/overview` - Overview metrics

### Sites & Cameras
- `GET /api/sites` - List all sites
- `POST /api/sites` - Create new site
- `GET /api/cameras` - List all cameras
- `POST /api/cameras` - Create new camera

### Alerts
- `GET /api/alerts` - List alerts
- `POST /api/alerts/{id}/resolve` - Mark alert as resolved

### Analytics
- `GET /api/analytics/traffic` - Traffic analytics
- `GET /api/exports/traffic.csv` - Export traffic data (CSV)

### Vision Integration
- `POST /api/ingest/events` - Ingest vision engine event batches (internal, requires `X-API-Key`)

See [docs/api.md](docs/api.md) for complete reference.

## File Structure

```
sen-trafic-ai/
├── backend-api/               # FastAPI backend service
│   ├── app/
│   │   ├── main.py
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   └── db.py
│   ├── migrations/            # Alembic migrations
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── vision-engine/             # YOLO detection & tracking
│   ├── main.py
│   ├── detector.py
│   ├── tracker.py
│   ├── analytics.py
│   ├── Dockerfile
│   └── requirements.txt
├── dashboard/                 # Next.js frontend
│   ├── app/
│   ├── components/
│   ├── pages/
│   ├── public/
│   ├── styles/
│   ├── Dockerfile
│   └── package.json
├── docs/                      # Documentation
│   ├── architecture.md
│   ├── api.md
│   ├── deployment.md
│   ├── vision-pipeline.md
│   └── roadmap.md
├── scripts/                   # Helper scripts
│   ├── dev-up.sh
│   ├── dev-down.sh
│   ├── seed-demo.sh
│   └── run-vision-demo.sh
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Development Workflow

### Starting Development

```bash
./scripts/dev-up.sh
```

This will:
1. Start Docker Compose services
2. Wait for PostgreSQL to be ready
3. Run database migrations
4. Seed demo data if needed

### Stopping Development

```bash
./scripts/dev-down.sh
```

### Running Vision Engine Locally

```bash
./scripts/run-vision-demo.sh
```

### Seeding Demo Data

```bash
./scripts/seed-demo.sh
```

## Configuration

### Database

PostgreSQL automatically initializes with the configured database and user. Migrations run automatically on service startup.

### Redis

Redis is used for caching, rate limiting, and real-time metric aggregation. Connection string: `redis://redis:6379/0`

### Vision Engine

Configure video sources in the vision engine:

```env
# File input
VISION_SOURCE=samples/videos/demo.mp4

# RTSP stream
VISION_SOURCE=rtsp://camera-ip:554/stream

# Local camera
VISION_SOURCE=0
```

## API Documentation

Once services are running, access interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

### Code Style

- **Python**: PEP 8, formatted with Black, linted with Ruff
- **TypeScript**: ESLint, Prettier
- **Commits**: Conventional Commits format

### Development Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Format code: `black . && npm run format`
4. Lint: `ruff check . && npm run lint`
5. Commit: `git commit -m "feat: your feature description"`
6. Push and create pull request

### Testing

```bash
# Backend tests
cd backend-api
pytest

# Frontend tests
cd dashboard
npm test

# Integration tests
docker-compose up
pytest integration-tests/
```

## Deployment

See [docs/deployment.md](docs/deployment.md) for production deployment guide including:
- VPS setup and configuration
- Docker deployment
- SSL/TLS configuration
- Nginx reverse proxy setup
- Monitoring and logging
- Backup strategies

## Monitoring & Logging

- **Application Logs**: Check with `docker-compose logs <service>`
- **Health Endpoints**: `GET /api/health` for backend
- **Camera Monitoring**: `GET /api/cameras/{id}/traffic`
- **Analytics**: `GET /api/analytics/traffic` and `GET /api/analytics/distribution`

## Troubleshooting

### Services not starting

```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose build --no-cache

# Reset volumes
docker-compose down -v
docker-compose up -d
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check network connectivity
docker-compose exec backend-api ping postgres
```

### Vision engine not processing

```bash
# Check GPU availability (if using GPU)
docker-compose exec vision-engine nvidia-smi

# Check vision engine logs
docker-compose logs vision-engine
```

## Performance Tuning

### Vision Engine
- Adjust YOLO model size (nano, small, medium) based on hardware
- Configure batch size and confidence thresholds
- Enable GPU inference for better throughput

### Backend API
- Configure worker count based on CPU cores
- Adjust Redis cache TTLs
- Enable CORS only for trusted domains

### Database
- Regular vacuum and analyze operations
- Index management
- Connection pooling configuration

## Security

- JWT tokens expire after 24 hours
- API endpoints require authentication (except /health)
- Sensitive data is never logged
- All secrets must be changed in production
- Use HTTPS in production
- Enable CORS only for trusted origins

## License

Proprietary - SEN TRAFIC AI

## Contact & Support

For issues, questions, or contributions, please contact the development team.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for detailed product roadmap and planned features.

---

**Version**: 1.0.0-MVP
**Last Updated**: 2026-04-11
