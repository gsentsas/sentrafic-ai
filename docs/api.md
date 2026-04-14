# SEN TRAFIC AI - API Reference (Current Implementation)

This document reflects the backend routes currently implemented in `backend-api`.

## Base URL

- Local: `http://localhost:8000`
- API prefix: `/api`

## Authentication Model

- JWT Bearer token:
  - Required on most business routes.
  - Obtained via `POST /api/auth/login`.
- Vision ingest API key:
  - Required only on `POST /api/ingest/events`.
  - Header: `X-API-Key: <VISION_API_KEY>`.

## Response Model

The API returns JSON objects/lists directly (no global wrapper like `{ data, status, message }`).

Error shape:

```json
{
  "detail": "Error message"
}
```

## Route Protection Summary

- Public:
  - `GET /health`
  - `GET /`
  - `POST /api/auth/login`
  - `POST /api/auth/register`
  - `GET /api/health/`
- API key only:
  - `POST /api/ingest/events`
- JWT required:
  - `sites`, `cameras`, `dashboard`, `analytics`, `alerts`, `exports`
- JWT + role constraints:
  - `users` routes (admin checks on management actions)

## Main Endpoints

### Auth

- `POST /api/auth/login`
  - Body:
    ```json
    {
      "email": "admin@sentrafic.sn",
      "password": "admin123"
    }
    ```
  - Response:
    ```json
    {
      "access_token": "jwt",
      "token_type": "bearer"
    }
    ```

- `POST /api/auth/register`
  - Query params: `email`, `password`, `full_name`
  - Creates a `viewer` user.

### Health

- `GET /api/health/`
- `GET /health`

### Sites (JWT)

- `GET /api/sites/?skip=0&limit=100&site_type=intersection`
- `POST /api/sites/`
- `GET /api/sites/{site_id}`
- `PUT /api/sites/{site_id}`

### Cameras (JWT)

- `GET /api/cameras/?skip=0&limit=100&site_id=<uuid>`
- `POST /api/cameras/`
- `GET /api/cameras/{camera_id}`
- `PUT /api/cameras/{camera_id}`
- `GET /api/cameras/{camera_id}/traffic?hours=24`

### Dashboard (JWT)

- `GET /api/dashboard/overview`

### Analytics (JWT)

- `GET /api/analytics/traffic?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&granularity=hour`
- `GET /api/analytics/summary?period_minutes=60`
- `GET /api/analytics/trend?camera_id=<uuid>&hours=24`
- `GET /api/analytics/distribution?period_hours=24`

### Alerts (JWT)

- `GET /api/alerts/?is_resolved=false&severity=critical&skip=0&limit=100`
- `GET /api/alerts/{alert_id}`
- `POST /api/alerts/{alert_id}/resolve`
  - Body:
    ```json
    {}
    ```
  - Optional fields:
    ```json
    {
      "resolved_by": "uuid",
      "note": "optional note"
    }
    ```

### Exports (JWT)

- `GET /api/exports/traffic.csv?camera_id=<uuid>&site_id=<uuid>&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

### Ingest (API key)

- `POST /api/ingest/events`
  - Headers:
    - `X-API-Key: <VISION_API_KEY>`
    - `Content-Type: application/json`
  - Body:
    ```json
    {
      "events": [
        {
          "camera_id": "uuid",
          "timestamp": "2026-04-14T08:00:00Z",
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

### Users (JWT)

- `GET /api/users/me`
- `PUT /api/users/me/password`
- `GET /api/users/` (admin)
- `POST /api/users/` (admin)
- `PUT /api/users/{user_id}` (admin)

---

Last updated: 2026-04-14
