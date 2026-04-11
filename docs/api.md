# SEN TRAFIC AI - API Reference

## Overview

The SEN TRAFIC AI Backend API is a RESTful API built with FastAPI that provides complete access to traffic monitoring, analytics, and management functionality. All requests use JSON for request and response bodies.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.sentrafic.sn`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Tokens are obtained via the login endpoint and expire after 24 hours.

## Response Format

All responses use standard HTTP status codes and JSON format:

```json
{
  "data": {},
  "message": "Success",
  "status": "success"
}
```

Error responses:

```json
{
  "detail": "Error message",
  "status": "error"
}
```

## Rate Limiting

Rate limits are applied to all endpoints:
- 100 requests per minute for authenticated users
- 20 requests per minute for public endpoints

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 98
X-RateLimit-Reset: 1649827200
```

## Endpoints

### Authentication

#### Login
Create a new session and receive JWT token.

```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK)**:
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "operator"
    }
  },
  "message": "Login successful",
  "status": "success"
}
```

**Errors**:
- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Email or password incorrect

---

#### Logout
Invalidate current session.

```
POST /api/auth/logout
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "message": "Logout successful",
  "status": "success"
}
```

---

#### Refresh Token
Get a new access token using current token.

```
POST /api/auth/refresh
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  },
  "message": "Token refreshed",
  "status": "success"
}
```

---

### System

#### Health Check
Check API health and dependencies.

```
GET /api/health
```

**Response (200 OK)**:
```json
{
  "data": {
    "status": "healthy",
    "services": {
      "postgres": "healthy",
      "redis": "healthy"
    },
    "timestamp": "2026-04-11T10:30:45Z"
  },
  "message": "System healthy",
  "status": "success"
}
```

**Response (503 Service Unavailable)**:
```json
{
  "data": {
    "status": "unhealthy",
    "services": {
      "postgres": "unhealthy",
      "redis": "healthy"
    },
    "timestamp": "2026-04-11T10:30:45Z"
  },
  "message": "System unhealthy",
  "status": "error"
}
```

---

### Dashboard

#### Dashboard Overview
Get real-time overview metrics for the dashboard.

```
GET /api/dashboard/overview
Authorization: Bearer <token>
```

**Query Parameters**:
- `site_id` (optional): Filter by specific site UUID

**Response (200 OK)**:
```json
{
  "data": {
    "total_vehicles_24h": 3250,
    "active_cameras": 12,
    "average_congestion": 0.45,
    "alerts_today": 8,
    "top_sites": [
      {
        "site_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Plateau",
        "vehicle_count": 450,
        "congestion_level": 0.65
      }
    ],
    "recent_alerts": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "camera_id": "550e8400-e29b-41d4-a716-446655440002",
        "type": "congestion",
        "severity": "high",
        "triggered_at": "2026-04-11T10:15:00Z"
      }
    ]
  },
  "message": "Overview retrieved",
  "status": "success"
}
```

---

### Sites

#### List All Sites
Retrieve all traffic monitoring sites.

```
GET /api/sites
Authorization: Bearer <token>
```

**Query Parameters**:
- `skip` (optional, default: 0): Number of records to skip for pagination
- `limit` (optional, default: 20): Number of records to return
- `region` (optional): Filter by region name

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Plateau",
      "region": "Dakar",
      "city": "Dakar",
      "description": "Main intersection near Presidential Palace",
      "location": {
        "latitude": 14.6928,
        "longitude": -17.0469
      },
      "camera_count": 4,
      "created_at": "2026-01-15T08:00:00Z",
      "updated_at": "2026-04-11T10:30:00Z"
    }
  ],
  "total": 12,
  "message": "Sites retrieved",
  "status": "success"
}
```

---

#### Create Site
Add a new traffic monitoring site.

```
POST /api/sites
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Medina",
  "region": "Dakar",
  "city": "Dakar",
  "description": "Main avenue traffic monitoring",
  "latitude": 14.7167,
  "longitude": -17.0667
}
```

**Response (201 Created)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "name": "Medina",
    "region": "Dakar",
    "city": "Dakar",
    "description": "Main avenue traffic monitoring",
    "location": {
      "latitude": 14.7167,
      "longitude": -17.0667
    },
    "camera_count": 0,
    "created_at": "2026-04-11T10:30:45Z",
    "updated_at": "2026-04-11T10:30:45Z"
  },
  "message": "Site created",
  "status": "success"
}
```

**Errors**:
- `400 Bad Request`: Invalid site data
- `409 Conflict`: Site name already exists

---

#### Get Site Details
Retrieve detailed information about a specific site.

```
GET /api/sites/{site_id}
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Plateau",
    "region": "Dakar",
    "city": "Dakar",
    "description": "Main intersection near Presidential Palace",
    "location": {
      "latitude": 14.6928,
      "longitude": -17.0469
    },
    "cameras": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "North Lane",
        "is_active": true,
        "health_status": "healthy"
      }
    ],
    "created_at": "2026-01-15T08:00:00Z",
    "updated_at": "2026-04-11T10:30:00Z"
  },
  "message": "Site retrieved",
  "status": "success"
}
```

---

### Cameras

#### List All Cameras
Retrieve all cameras across all sites.

```
GET /api/cameras
Authorization: Bearer <token>
```

**Query Parameters**:
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 20): Results per page
- `site_id` (optional): Filter by site
- `is_active` (optional): Filter by active status (true/false)
- `health_status` (optional): Filter by health (healthy/degraded/offline)

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "site_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "North Lane",
      "camera_type": "fixed",
      "ip_address": "192.168.1.100",
      "rtsp_url": "rtsp://192.168.1.100:554/stream",
      "latitude": 14.6930,
      "longitude": -17.0470,
      "angle": 45,
      "is_active": true,
      "health_status": "healthy",
      "last_health_check": "2026-04-11T10:29:00Z"
    }
  ],
  "total": 12,
  "message": "Cameras retrieved",
  "status": "success"
}
```

---

#### Create Camera
Add a new camera to a site.

```
POST /api/cameras
Authorization: Bearer <token>
Content-Type: application/json

{
  "site_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "South Lane",
  "camera_type": "fixed",
  "ip_address": "192.168.1.101",
  "rtsp_url": "rtsp://192.168.1.101:554/stream",
  "latitude": 14.6920,
  "longitude": -17.0470,
  "angle": 225
}
```

**Response (201 Created)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "site_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "South Lane",
    "camera_type": "fixed",
    "ip_address": "192.168.1.101",
    "rtsp_url": "rtsp://192.168.1.101:554/stream",
    "latitude": 14.6920,
    "longitude": -17.0470,
    "angle": 225,
    "is_active": true,
    "health_status": "healthy",
    "last_health_check": "2026-04-11T10:30:45Z"
  },
  "message": "Camera created",
  "status": "success"
}
```

---

#### Get Camera Health
Retrieve detailed health information for a camera.

```
GET /api/cameras/{camera_id}/health
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "data": {
    "camera_id": "550e8400-e29b-41d4-a716-446655440002",
    "health_status": "healthy",
    "last_check": "2026-04-11T10:29:00Z",
    "is_responsive": true,
    "frame_rate": 30,
    "latency_ms": 45,
    "uptime_hours": 720,
    "recent_checks": [
      {
        "timestamp": "2026-04-11T10:29:00Z",
        "is_responsive": true,
        "frame_rate": 30,
        "latency_ms": 45
      }
    ]
  },
  "message": "Health retrieved",
  "status": "success"
}
```

---

### Alerts

#### List Alerts
Retrieve all system alerts.

```
GET /api/alerts
Authorization: Bearer <token>
```

**Query Parameters**:
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 20): Results per page
- `status` (optional): Filter by status (active/acknowledged/resolved)
- `severity` (optional): Filter by severity (low/medium/high/critical)
- `camera_id` (optional): Filter by camera
- `start_date` (optional): ISO 8601 start timestamp
- `end_date` (optional): ISO 8601 end timestamp

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "camera_id": "550e8400-e29b-41d4-a716-446655440002",
      "camera_name": "North Lane",
      "alert_type": "congestion",
      "severity": "high",
      "description": "High traffic congestion detected",
      "status": "active",
      "triggered_at": "2026-04-11T10:15:00Z",
      "resolved_at": null,
      "metadata": {
        "congestion_level": 0.85,
        "vehicle_count": 120
      }
    }
  ],
  "total": 8,
  "message": "Alerts retrieved",
  "status": "success"
}
```

---

#### Resolve Alert
Mark an alert as resolved.

```
POST /api/alerts/{alert_id}/resolve
Authorization: Bearer <token>
Content-Type: application/json

{
  "notes": "Congestion cleared after incident resolution"
}
```

**Response (200 OK)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440005",
    "status": "resolved",
    "resolved_at": "2026-04-11T10:35:00Z",
    "resolved_by": "550e8400-e29b-41d4-a716-446655440100"
  },
  "message": "Alert resolved",
  "status": "success"
}
```

---

### Analytics

#### Traffic Analytics
Retrieve aggregated traffic metrics.

```
GET /api/analytics/traffic
Authorization: Bearer <token>
```

**Query Parameters**:
- `camera_id` (required): Camera UUID
- `start_date` (required): ISO 8601 start timestamp
- `end_date` (required): ISO 8601 end timestamp
- `granularity` (optional, default: hourly): hourly/daily/weekly
- `metric` (optional): Specific metric to retrieve

**Response (200 OK)**:
```json
{
  "data": {
    "camera_id": "550e8400-e29b-41d4-a716-446655440002",
    "camera_name": "North Lane",
    "start_date": "2026-04-10T00:00:00Z",
    "end_date": "2026-04-11T00:00:00Z",
    "granularity": "hourly",
    "metrics": [
      {
        "timestamp": "2026-04-10T00:00:00Z",
        "vehicle_count": 125,
        "line_crossings": 45,
        "zone_occupancy": 0.32,
        "congestion_level": 0.25,
        "classifications": {
          "car": 85,
          "truck": 25,
          "motorcycle": 15
        }
      }
    ]
  },
  "message": "Analytics retrieved",
  "status": "success"
}
```

---

### Data Export

#### Export Traffic Data
Export traffic data in CSV format.

```
GET /api/exports/traffic.csv
Authorization: Bearer <token>
```

**Query Parameters**:
- `camera_id` (required): Camera UUID
- `start_date` (required): ISO 8601 start timestamp
- `end_date` (required): ISO 8601 end timestamp
- `metrics` (optional): Comma-separated metric names

**Response (200 OK)**:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="traffic-2026-04-11.csv"

timestamp,vehicle_count,line_crossings,zone_occupancy,congestion_level,car,truck,motorcycle
2026-04-10T00:00:00Z,125,45,0.32,0.25,85,25,15
2026-04-10T01:00:00Z,98,38,0.28,0.20,72,18,8
```

---

### Vision Engine Integration (Internal)

#### Ingest Events
Receive events from Vision Engine. Internal use only.

```
POST /api/ingest/events
Content-Type: application/json
X-API-Key: <vision-api-key>

{
  "camera_id": "550e8400-e29b-41d4-a716-446655440002",
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

**Response (202 Accepted)**:
```json
{
  "data": {
    "event_id": "550e8400-e29b-41d4-a716-446655440006",
    "camera_id": "550e8400-e29b-41d4-a716-446655440002",
    "status": "accepted"
  },
  "message": "Event ingested",
  "status": "success"
}
```

---

## Error Responses

### Common Error Codes

**400 Bad Request**
```json
{
  "detail": "Invalid request body",
  "status": "error"
}
```

**401 Unauthorized**
```json
{
  "detail": "Invalid or expired token",
  "status": "error"
}
```

**403 Forbidden**
```json
{
  "detail": "Insufficient permissions",
  "status": "error"
}
```

**404 Not Found**
```json
{
  "detail": "Resource not found",
  "status": "error"
}
```

**429 Too Many Requests**
```json
{
  "detail": "Rate limit exceeded",
  "status": "error"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error",
  "status": "error"
}
```

---

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:

```
GET /api/sites?skip=0&limit=20
```

Response includes total count:
```json
{
  "data": [...],
  "total": 50,
  "skip": 0,
  "limit": 20
}
```

---

## Date/Time Format

All timestamps use ISO 8601 format with UTC timezone:
```
2026-04-11T10:30:45Z
```

---

## API Client Examples

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Get alerts
curl -X GET "http://localhost:8000/api/alerts?status=active" \
  -H "Authorization: Bearer <token>"
```

### Python (requests)

```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'email': 'user@example.com', 'password': 'password123'}
)
token = response.json()['data']['access_token']

# Get alerts
response = requests.get(
    'http://localhost:8000/api/alerts',
    params={'status': 'active'},
    headers={'Authorization': f'Bearer {token}'}
)
alerts = response.json()['data']
```

### JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { data } = await loginResponse.json();
const token = data.access_token;

// Get alerts
const alertsResponse = await fetch(
  'http://localhost:8000/api/alerts?status=active',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
const alerts = await alertsResponse.json();
```

---

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

---

**API Version**: 1.0.0
**Last Updated**: 2026-04-11
