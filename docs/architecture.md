# SEN TRAFIC AI - System Architecture

## System Overview

SEN TRAFIC AI is a distributed computer vision platform designed for real-time traffic analysis in Senegal. The system processes video streams from fixed traffic cameras, performs AI-driven vehicle detection and tracking, aggregates traffic metrics, and provides actionable insights through a web-based dashboard.

## Architecture Philosophy

The system follows a microservices architecture with clear separation of concerns:

- **Vision Engine**: Stateless video processing service focused on detection and tracking
- **Backend API**: Centralized data layer with business logic and persistence
- **Frontend Dashboard**: User-facing interface for visualization and analysis
- **Infrastructure**: Containerized deployment with managed databases and caching

## Four-Service Architecture

### 1. Vision Engine (`vision-engine`)

**Purpose**: Real-time video processing and traffic metrics computation

**Technology Stack**:
- Python 3.10+
- YOLOv8 for object detection
- ByteTrack for multi-object tracking
- OpenCV for image processing
- NumPy/SciPy for numerical computation

**Responsibilities**:
- Consume video streams from cameras (files, RTSP, USB cameras)
- Run YOLO object detection on frames
- Track detected objects across frames using ByteTrack
- Compute traffic metrics (line crossings, zone occupancy, density)
- Publish metrics to Backend API via HTTP
- Monitor and report camera health status

**Key Features**:
- Configurable confidence thresholds
- Support for multiple camera sources
- GPU acceleration (optional, falls back to CPU)
- Graceful error handling and restart capability
- Metric batching and buffering

**Output Format**: JSON events published to `/api/ingest/events`

```json
{
  "camera_id": 1,
  "timestamp": "2026-04-11T10:30:45Z",
  "metrics": {
    "vehicle_count": 42,
    "line_crossings": 15,
    "zone_occupancy": 0.45,
    "classifications": {
      "car": 28,
      "truck": 10,
      "motorcycle": 4
    }
  }
}
```

### 2. Backend API (`backend-api`)

**Purpose**: Central application logic, data persistence, and API gateway

**Technology Stack**:
- FastAPI (Python 3.10+)
- PostgreSQL 14 for persistent storage
- SQLAlchemy ORM
- Pydantic for data validation
- JWT for authentication
- Redis for caching and session management

**Responsibilities**:
- Ingest events from Vision Engine
- Manage user authentication and authorization
- CRUD operations for sites, cameras, and alerts
- Compute aggregated analytics
- Generate reports and exports
- Manage camera configuration and health monitoring
- Provide RESTful API for frontend and external clients
- Event-driven alerting based on traffic conditions

**Database Schema**:

```
User
├── id (UUID)
├── email (VARCHAR, unique)
├── password_hash
├── full_name
├── role (ENUM: admin, operator, analyst)
├── created_at
└── updated_at

Site
├── id (UUID)
├── name (VARCHAR)
├── location (GEOMETRY)
├── region (VARCHAR)
├── city (VARCHAR)
├── description
└── created_at

Camera
├── id (UUID)
├── site_id (FK)
├── name (VARCHAR)
├── camera_type (ENUM: fixed, ptz, thermal)
├── ip_address (VARCHAR)
├── rtsp_url (VARCHAR)
├── latitude
├── longitude
├── angle (INT)
├── is_active
├── health_status (ENUM: healthy, degraded, offline)
└── last_health_check

TrafficAggregate
├── id (UUID)
├── camera_id (FK)
├── timestamp
├── window_size (INT, seconds)
├── vehicle_count
├── line_crossings
├── zone_occupancy
├── vehicle_classifications (JSONB)
├── average_speed (optional)
├── congestion_level
└── created_at

Alert
├── id (UUID)
├── camera_id (FK)
├── alert_type (ENUM: congestion, accident, anomaly)
├── severity (ENUM: low, medium, high, critical)
├── description
├── triggered_at
├── resolved_at
├── status (ENUM: active, acknowledged, resolved)
└── metadata (JSONB)

CameraHealthCheck
├── id (UUID)
├── camera_id (FK)
├── timestamp
├── is_responsive
├── frame_rate
├── latency_ms
├── error_message (nullable)
└── created_at
```

**Key Endpoints**:
- `/api/auth/*` - Authentication
- `/api/sites/*` - Site management
- `/api/cameras/*` - Camera management
- `/api/alerts/*` - Alert management
- `/api/analytics/*` - Analytics and reporting
- `/api/ingest/*` - Event ingestion from Vision Engine

### 3. Dashboard (`dashboard`)

**Purpose**: User interface for traffic monitoring and analysis

**Technology Stack**:
- Next.js 14 (React 18+)
- TypeScript
- Tailwind CSS
- Recharts for data visualization
- Zustand or Context API for state management
- Axios for HTTP client

**Key Pages**:
- `/` - Dashboard overview with real-time metrics
- `/sites` - Site management
- `/cameras` - Camera list and configuration
- `/analytics` - Detailed traffic analytics
- `/alerts` - Alert management and history
- `/reports` - Report generation and exports
- `/settings` - User and system settings

**Features**:
- Real-time metric updates via polling or WebSocket
- Interactive charts and visualizations
- Responsive design for desktop and tablet
- User authentication and role-based access control
- Export functionality (CSV, PDF)
- Mobile-friendly responsive layout

### 4. Infrastructure (`infra`)

**Components**:
- **PostgreSQL**: Primary data store with volume persistence
- **Redis**: Cache layer and session store
- **Docker Compose**: Local development orchestration
- **Docker**: Container images for all services

**Features**:
- Health checks for all services
- Automatic restart policies
- Volume management for data persistence
- Network isolation with custom bridge network
- Resource limits and requests
- Environment-based configuration

## Data Flow

### Vision-to-Backend Flow

```
Camera Feed
    ↓
Vision Engine (Detection & Tracking)
    ↓
Frame-level Metrics
    ↓
Batching & Aggregation
    ↓
HTTP POST /api/ingest/events
    ↓
Backend API Receives Event
    ↓
Validate & Store in PostgreSQL
    ↓
Update Redis Cache
    ↓
Trigger Alerting Logic
    ↓
Event published to subscribed clients
```

### Backend-to-Dashboard Flow

```
Dashboard Web Browser
    ↓
HTTP Request to Backend API
    ↓
JWT Authentication
    ↓
Query PostgreSQL or Redis Cache
    ↓
Format Response (JSON)
    ↓
HTTP Response
    ↓
Dashboard Updates UI
    ↓
Render charts/tables
```

### Real-time Update Flow (Optional WebSocket)

```
Dashboard (WebSocket Client)
    ↓
connect to /ws/analytics
    ↓
Backend (WebSocket Server)
    ↓
Listen to new TrafficAggregate events
    ↓
Broadcast to connected clients
    ↓
Dashboard receives updates
    ↓
Update UI without page reload
```

## Technology Choices & Rationale

### Why YOLO?
- State-of-the-art accuracy for vehicle detection
- Real-time performance suitable for streaming
- Multiple size variants (nano to xlarge) for hardware flexibility
- Extensive community support and pre-trained models

### Why ByteTrack?
- Efficient multi-object tracking without complex re-identification
- Low computational overhead
- Robust to occlusions and viewpoint changes
- Suitable for high-density traffic scenarios

### Why FastAPI?
- High performance with async/await support
- Automatic API documentation (Swagger/ReDoc)
- Built-in data validation with Pydantic
- Easy integration with async database drivers
- Strong type hints for developer experience

### Why PostgreSQL?
- ACID compliance for data integrity
- PostGIS extension for spatial queries (camera locations)
- JSONB for flexible metadata storage
- Proven reliability and performance at scale

### Why Redis?
- High-speed caching for frequently accessed data
- Distributed session management
- Publish/Subscribe for real-time updates
- Leaderboards and sorted sets for analytics

### Why Next.js?
- Server-side rendering for performance and SEO
- File-based routing simplifying navigation
- Built-in API routes for backend integration
- Incremental Static Regeneration for scalability
- Excellent TypeScript support

## Security Model

### Authentication & Authorization

- JWT tokens issued on login, stored in HttpOnly cookies
- Tokens expire after 24 hours (configurable)
- Refresh token mechanism for extended sessions
- Role-based access control (RBAC): Admin, Operator, Analyst

### Data Security

- All sensitive data encrypted at rest (database-level)
- HTTPS required in production
- API requests validated and sanitized
- SQL injection prevented via SQLAlchemy ORM
- CORS policies restrict cross-origin requests

### API Security

- Rate limiting on public endpoints
- Request size limits to prevent abuse
- Authentication required for all endpoints except `/health`
- Audit logging for sensitive operations
- API key authentication for Vision Engine

## Deployment Architecture

### Development
- Single Docker Compose stack on local machine
- All services on local network bridge
- Direct API URLs (localhost:8000)
- Debug logging enabled

### Production
- Kubernetes or Docker Swarm for orchestration
- Separate nodes for each service tier
- Load balancer (nginx or cloud-native)
- SSL/TLS termination at ingress
- Separate read replicas for PostgreSQL
- Redis cluster for high availability
- CloudFlare or similar for DDoS protection
- Centralized logging (ELK, Datadog, etc.)

## Scalability Considerations

### Horizontal Scaling
- Vision Engine: Stateless, can run multiple instances per camera
- Backend API: Stateless, can run behind load balancer
- Dashboard: Static assets can be served from CDN
- Database: Read replicas for scaling reads, primary for writes

### Vertical Scaling
- Configure worker counts in Backend API
- Adjust batch sizes in Vision Engine
- YOLO model size selection (nano to xlarge)
- Redis memory limits

### Caching Strategy
- Dashboard overview: 5-minute cache
- Analytics queries: 10-minute cache
- Camera health: 1-minute cache
- User data: Session-based cache

## Monitoring & Observability

### Health Checks
- PostgreSQL: TCP health check
- Redis: PING health check
- Backend API: HTTP `/api/health` endpoint
- Vision Engine: Periodic health reports

### Metrics
- Vision Engine: FPS, detection latency, GPU utilization
- Backend API: Request count, error rate, response time
- Database: Connection pool usage, query performance
- Dashboard: Page load time, error rate

### Logging
- Structured JSON logging for all services
- Centralized log aggregation (optional)
- Application logs in `/app/logs/` directories
- Access logs for API requests

## Future Enhancements

### Phase 1.1
- WebSocket support for real-time metric streaming
- Heatmap visualization for traffic distribution
- Multi-camera synchronized view

### Phase 1.2
- Incident detection (accidents, congestion)
- SMS/Email alert notifications
- Integration with traffic management systems

### Phase 2.0
- ML-based anomaly detection
- Predictive traffic flow modeling
- Incident forecasting

### Phase 3.0
- Mobile application for field operators
- Public API with rate limiting
- Webhook support for external integrations

---

**Document Version**: 1.0.0
**Last Updated**: 2026-04-11
