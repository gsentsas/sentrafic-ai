# SEN TRAFIC AI - Backend API

FastAPI backend for computer vision-based traffic analysis platform serving real-time traffic detection, monitoring, and analytics.

## Overview

This is the backend API service for SEN TRAFIC AI MVP, a platform that processes video streams from fixed traffic cameras to detect and analyze vehicle and pedestrian flows, generate congestion alerts, and provide analytics dashboards.

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL 13+ (SQLAlchemy ORM)
- **Cache**: Redis
- **Authentication**: JWT with Python-Jose
- **Testing**: Pytest + pytest-asyncio

## Features

- Real-time traffic event ingestion from vision engine
- Traffic aggregation by camera, site, and time period
- Congestion detection and alerting
- Camera health monitoring
- Dashboard analytics and reporting
- CSV export functionality
- Multi-role access control (admin, operator, viewer)
- JWT-based authentication

## Project Structure

```
backend-api/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings from environment
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── security.py         # JWT and password utilities
│   │   └── logging.py          # Logging configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── site.py
│   │   ├── camera.py
│   │   ├── traffic_aggregate.py
│   │   ├── alert.py
│   │   └── camera_health.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── site.py
│   │   ├── camera.py
│   │   ├── traffic.py
│   │   ├── alert.py
│   │   └── ingest.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── site_service.py
│   │   ├── camera_service.py
│   │   ├── traffic_service.py
│   │   ├── alert_service.py
│   │   ├── ingest_service.py
│   │   ├── export_service.py
│   │   └── health_service.py
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── health.py
│   │       ├── sites.py
│   │       ├── cameras.py
│   │       ├── dashboard.py
│   │       ├── analytics.py
│   │       ├── alerts.py
│   │       ├── ingest.py
│   │       └── exports.py
│   ├── db/
│   │   ├── base.py
│   │   └── seed.py
│   └── main.py
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_sites.py
│   ├── test_ingest.py
│   └── test_dashboard.py
├── requirements.txt
├── .env.example
├── alembic.ini
└── README.md
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your local database and Redis URLs
   ```

5. Create PostgreSQL database:
   ```bash
   createdb sentrafic
   ```

6. Run migrations:
   ```bash
   alembic upgrade head
   ```

7. Seed the database (optional):
   ```bash
   python -c "from app.db.seed import seed_database; from app.core.database import SessionLocal; seed_database(SessionLocal())"
   ```

## Running the Application

### Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

Run specific test file:
```bash
pytest tests/test_health.py -v
```

## API Endpoints

Auth requirements:
- Public: `/api/auth/login`, `/api/auth/register`, `/api/health`, `/health`
- API key (`X-API-Key`): `/api/ingest/events`
- JWT required: sites, cameras, dashboard, analytics, alerts, exports, users

### Authentication
- `POST /api/auth/login` - Authenticate user and get JWT token

### Health
- `GET /api/health` - System health check (no auth required)

### Sites
- `GET /api/sites/` - List all sites
- `POST /api/sites/` - Create new site
- `GET /api/sites/{id}` - Get site details
- `PUT /api/sites/{id}` - Update site

### Cameras
- `GET /api/cameras/` - List cameras (optional: ?site_id=...)
- `POST /api/cameras/` - Create new camera
- `GET /api/cameras/{id}` - Get camera details

### Dashboard
- `GET /api/dashboard/overview` - Dashboard overview with key metrics

### Analytics
- `GET /api/analytics/traffic` - Traffic aggregates with filters
- `GET /api/analytics/distribution` - Vehicle class distribution

### Alerts
- `GET /api/alerts/` - List alerts with filters
- `POST /api/alerts/{id}/resolve` - Resolve an alert

### Ingest (Vision Engine Integration)
- `POST /api/ingest/events` - Receive detection events batch from vision engine

### Exports
- `GET /api/exports/traffic.csv` - Download traffic data as CSV

## Environment Variables

See `.env.example` for all required variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - Secret key for JWT signing
- `JWT_ALGORITHM` - Algorithm for JWT (HS256)
- `JWT_EXPIRE_MINUTES` - JWT expiration time in minutes
- `ADMIN_EMAIL` - Default admin email
- `ADMIN_PASSWORD` - Default admin password

## Data Models

### Classes Detected
- car
- bus
- truck
- motorcycle
- person

### Site Types
- intersection
- highway
- parking
- logistics
- bus_station
- industrial

### Alert Types
- congestion
- stalled_vehicle
- camera_offline
- zone_overflow

### Congestion Levels
- free
- moderate
- heavy
- blocked

### User Roles
- admin
- operator
- viewer

## Vision Engine Integration

The `/api/ingest/events` endpoint receives detection batches from the vision engine. Expected payload format:

```json
{
  "events": [
    {
      "camera_id": "uuid",
      "timestamp": "2024-01-15T10:30:00Z",
      "period_seconds": 300,
      "counts": {
        "car": 45,
        "bus": 3,
        "truck": 2,
        "motorcycle": 8,
        "person": 12
      },
      "avg_occupancy": 0.65,
      "congestion_level": "moderate"
    }
  ]
}
```

## Database Migrations

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Standard HTTP status codes are used:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Security

- JWT tokens expire after configured period (default: 480 minutes)
- Passwords are hashed using bcrypt
- CORS origins are configured via `CORS_ORIGINS` environment variable
- All database queries use parameterized statements (SQLAlchemy)
- Rate limiting should be added for production deployment

## Contributing

1. Create a feature branch
2. Make changes with tests
3. Run pytest to ensure all tests pass
4. Submit pull request

## License

Proprietary - SEN TRAFIC AI
