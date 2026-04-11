#!/bin/bash

# SEN TRAFIC AI - Demo Data Seeding Script
# Populates the database with sample data for demonstration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
ADMIN_EMAIL="admin@sentrafic.sn"
ADMIN_PASSWORD="admin123456"

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

check_backend() {
    print_header "Checking Backend Availability"

    print_info "Checking if backend is running at $BACKEND_URL..."

    for i in {1..10}; do
        if curl -s "$BACKEND_URL/api/health" > /dev/null 2>&1; then
            print_success "Backend is available"
            return 0
        fi
        print_info "Attempt $i/10 - Waiting for backend to be ready..."
        sleep 2
    done

    print_error "Backend is not responding at $BACKEND_URL"
    print_error "Make sure to run './scripts/dev-up.sh' first"
    exit 1
}

create_admin_user() {
    print_header "Creating Admin User"

    print_info "Creating admin user with email: $ADMIN_EMAIL"

    # Try to create the admin user
    response=$(curl -s -X POST "$BACKEND_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$ADMIN_EMAIL\",
            \"password\": \"$ADMIN_PASSWORD\",
            \"full_name\": \"System Administrator\",
            \"role\": \"admin\"
        }" 2>&1 || echo "{\"detail\": \"Failed\"}")

    # Check if user already exists or was created
    if echo "$response" | grep -q "already exists\|successfully\|created"; then
        print_success "Admin user created/verified"
    else
        print_warning "Could not create admin user (may already exist)"
    fi
}

login_and_get_token() {
    print_header "Authenticating"

    print_info "Logging in as $ADMIN_EMAIL..."

    token_response=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$ADMIN_EMAIL\",
            \"password\": \"$ADMIN_PASSWORD\"
        }")

    # Extract token from response
    TOKEN=$(echo "$token_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

    if [ -z "$TOKEN" ]; then
        print_error "Failed to authenticate"
        print_error "Response: $token_response"
        exit 1
    fi

    print_success "Authentication successful"
}

create_demo_sites() {
    print_header "Creating Demo Sites"

    # Define demo sites
    sites=(
        "Plateau|Dakar|Dakar|Main intersection near Presidential Palace|14.6928|-17.0469"
        "Medina|Dakar|Dakar|Main avenue traffic monitoring|14.7167|-17.0667"
        "Yoff|Dakar|Dakar|Airport approach road|14.7497|-17.1577"
        "Pikine|Dakar|Dakar|Highway entrance|14.7667|-17.1833"
        "Thiaroye|Dakar|Dakar|Industrial area traffic point|14.8333|-17.2000"
    )

    for site_data in "${sites[@]}"; do
        IFS='|' read -r name region city description latitude longitude <<< "$site_data"

        print_info "Creating site: $name"

        response=$(curl -s -X POST "$BACKEND_URL/api/sites" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "{
                \"name\": \"$name\",
                \"region\": \"$region\",
                \"city\": \"$city\",
                \"description\": \"$description\",
                \"latitude\": $latitude,
                \"longitude\": $longitude
            }")

        if echo "$response" | grep -q '"id"'; then
            site_id=$(echo "$response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
            print_success "Site created: $name (ID: $site_id)"

            # Store site ID for camera creation
            eval "${name// /_}_ID='$site_id'"
        else
            print_warning "Could not create site: $name"
        fi
    done
}

create_demo_cameras() {
    print_header "Creating Demo Cameras"

    # Get site IDs (fallback to creating a test site)
    if [ -z "$Plateau_ID" ]; then
        print_info "Creating default site for cameras..."
        response=$(curl -s -X POST "$BACKEND_URL/api/sites" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d '{
                "name": "Demo Site",
                "region": "Dakar",
                "city": "Dakar",
                "description": "Demo site for testing",
                "latitude": 14.6928,
                "longitude": -17.0469
            }')
        SITE_ID=$(echo "$response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    else
        SITE_ID="$Plateau_ID"
    fi

    # Define demo cameras
    cameras=(
        "North Lane|fixed|192.168.1.100|rtsp://192.168.1.100:554/stream|14.6930|-17.0470|45"
        "South Lane|fixed|192.168.1.101|rtsp://192.168.1.101:554/stream|14.6920|-17.0470|225"
        "East Lane|fixed|192.168.1.102|rtsp://192.168.1.102:554/stream|14.6925|-17.0450|90"
        "West Lane|fixed|192.168.1.103|rtsp://192.168.1.103:554/stream|14.6925|-17.0490|270"
    )

    for camera_data in "${cameras[@]}"; do
        IFS='|' read -r name type ip rtsp_url latitude longitude angle <<< "$camera_data"

        print_info "Creating camera: $name"

        response=$(curl -s -X POST "$BACKEND_URL/api/cameras" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "{
                \"site_id\": \"$SITE_ID\",
                \"name\": \"$name\",
                \"camera_type\": \"$type\",
                \"ip_address\": \"$ip\",
                \"rtsp_url\": \"$rtsp_url\",
                \"latitude\": $latitude,
                \"longitude\": $longitude,
                \"angle\": $angle
            }")

        if echo "$response" | grep -q '"id"'; then
            camera_id=$(echo "$response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
            print_success "Camera created: $name (ID: $camera_id)"
        else
            print_warning "Could not create camera: $name"
        fi
    done
}

create_demo_alerts() {
    print_header "Creating Demo Alerts"

    # Get first camera ID
    cameras_response=$(curl -s -X GET "$BACKEND_URL/api/cameras?limit=1" \
        -H "Authorization: Bearer $TOKEN")

    CAMERA_ID=$(echo "$cameras_response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

    if [ -z "$CAMERA_ID" ]; then
        print_warning "No cameras found, skipping alert creation"
        return 0
    fi

    # Create demo alerts
    alert_types=(
        "congestion|high|High traffic congestion detected"
        "anomaly|medium|Unusual traffic pattern detected"
        "congestion|critical|Critical congestion detected"
    )

    for alert_data in "${alert_types[@]}"; do
        IFS='|' read -r type severity description <<< "$alert_data"

        print_info "Creating alert: $description"

        response=$(curl -s -X POST "$BACKEND_URL/api/alerts" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "{
                \"camera_id\": \"$CAMERA_ID\",
                \"alert_type\": \"$type\",
                \"severity\": \"$severity\",
                \"description\": \"$description\"
            }")

        if echo "$response" | grep -q '"id"'; then
            alert_id=$(echo "$response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
            print_success "Alert created (ID: $alert_id)"
        else
            print_warning "Could not create alert: $description"
        fi
    done
}

create_demo_analytics() {
    print_header "Creating Demo Analytics Data"

    # Get first camera ID
    cameras_response=$(curl -s -X GET "$BACKEND_URL/api/cameras?limit=1" \
        -H "Authorization: Bearer $TOKEN")

    CAMERA_ID=$(echo "$cameras_response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

    if [ -z "$CAMERA_ID" ]; then
        print_warning "No cameras found, skipping analytics creation"
        return 0
    fi

    print_info "Creating sample traffic metrics for camera: $CAMERA_ID"

    # Create sample traffic data events
    for i in {1..10}; do
        vehicle_count=$((RANDOM % 100 + 20))
        crossings=$((RANDOM % 30 + 5))
        occupancy=$(echo "scale=2; $((RANDOM % 80))/100" | bc)

        response=$(curl -s -X POST "$BACKEND_URL/api/ingest/events" \
            -H "Content-Type: application/json" \
            -d "{
                \"camera_id\": \"$CAMERA_ID\",
                \"timestamp\": \"$(date -u +'%Y-%m-%dT%H:%M:%SZ')\",
                \"metrics\": {
                    \"vehicle_count\": $vehicle_count,
                    \"line_crossings\": $crossings,
                    \"zone_occupancy\": $occupancy,
                    \"classifications\": {
                        \"car\": $((vehicle_count * 70 / 100)),
                        \"truck\": $((vehicle_count * 15 / 100)),
                        \"motorcycle\": $((vehicle_count * 15 / 100))
                    }
                }
            }" 2>&1)

        if echo "$response" | grep -q '"status"\|"event_id"'; then
            print_success "Sample metric created ($i/10)"
        fi

        sleep 1
    done
}

print_summary() {
    print_header "Demo Data Creation Complete"

    echo -e ""
    echo -e "${GREEN}Demo data has been successfully created!${NC}"
    echo -e ""
    echo -e "You can now access the dashboard:"
    echo -e "  URL: ${GREEN}http://localhost:3000${NC}"
    echo -e "  Email: ${YELLOW}$ADMIN_EMAIL${NC}"
    echo -e "  Password: ${YELLOW}$ADMIN_PASSWORD${NC}"
    echo -e ""
    echo -e "API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e ""
}

main() {
    print_header "SEN TRAFIC AI - Demo Data Seeding"

    check_backend
    create_admin_user
    login_and_get_token
    create_demo_sites
    create_demo_cameras
    create_demo_alerts
    create_demo_analytics
    print_summary
}

# Run main function
main
