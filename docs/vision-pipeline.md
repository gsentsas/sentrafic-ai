# SEN TRAFIC AI - Vision Pipeline Documentation

## Overview

The Vision Engine is the core component responsible for real-time video processing, vehicle detection, tracking, and traffic metrics computation. It leverages state-of-the-art deep learning models and computer vision algorithms to extract actionable intelligence from video streams.

## Pipeline Architecture

```
Video Input
    ↓
Frame Extraction & Preprocessing
    ↓
YOLO Object Detection
    ↓
ByteTrack Multi-Object Tracking
    ↓
Metric Computation
    ├── Line Crossing Counting
    ├── Zone Occupancy Analysis
    ├── Vehicle Classification
    └── Speed Estimation (optional)
    ↓
Aggregation & Buffering
    ↓
HTTP Publishing to Backend API
```

## Core Components

### 1. Video Input Handling

The vision engine supports multiple input sources:

#### File Input
```python
VISION_SOURCE=samples/videos/demo.mp4
```
- Static video files
- Batch processing capability
- Useful for testing and demo purposes

#### RTSP Stream
```python
VISION_SOURCE=rtsp://192.168.1.100:554/stream
```
- Real-time network cameras
- IP cameras (Hikvision, Dahua, etc.)
- Persistent connection with automatic reconnection
- Most common in production deployments

#### USB Camera
```python
VISION_SOURCE=0
```
- Local USB webcams
- Camera index (0 for first camera, 1 for second, etc.)
- Limited use in production

#### HTTP Stream
```python
VISION_SOURCE=http://192.168.1.100:8080/stream
```
- HTTP motion JPEG stream
- Some IP cameras support HTTP streaming
- Lower overhead than RTSP

### 2. Frame Preprocessing

**Frame Extraction**:
- Extract frames at configured FPS
- Default: 30 FPS
- Configurable based on hardware and requirements

**Resizing**:
- Maintain aspect ratio
- Default resolution: 1280x720
- Reduces memory usage and improves processing speed

**Color Space Conversion**:
- Convert from BGR (OpenCV default) to RGB for YOLO
- Ensure consistent color representation

**Normalization**:
- Normalize pixel values to 0-1 range
- Prepare for neural network input

### 3. YOLO Object Detection

**Model Selection**:
```python
YOLO_MODEL=yolov8n.pt  # nano - fastest
YOLO_MODEL=yolov8s.pt  # small
YOLO_MODEL=yolov8m.pt  # medium
YOLO_MODEL=yolov8l.pt  # large
YOLO_MODEL=yolov8x.pt  # xlarge - most accurate
```

**Performance Characteristics**:

| Model | Size | Speed (CPU) | Speed (GPU) | Accuracy |
|-------|------|-------------|-------------|----------|
| nano  | 3.3M | ~100ms      | ~15ms       | 80.4%    |
| small | 11M  | ~250ms      | ~35ms       | 86.6%    |
| medium| 26M  | ~600ms      | ~65ms       | 88.6%    |
| large | 52M  | ~1200ms     | ~100ms      | 89.0%    |
| xlarge| 97M  | ~2200ms     | ~150ms      | 89.2%    |

**Configuration**:

```python
YOLO_CONFIDENCE=0.5      # Confidence threshold (0-1)
YOLO_IOU=0.45            # IOU threshold for NMS (0-1)
```

- **Confidence**: Minimum confidence required to report detection
  - Higher = fewer false positives, may miss real vehicles
  - Lower = more detections, more false positives
  - Recommended: 0.4-0.6 depending on camera angle and environment

- **IOU (Intersection over Union)**: Non-maximum suppression threshold
  - Controls suppression of overlapping boxes
  - Higher = keep more overlapping detections
  - Lower = more aggressive suppression
  - Recommended: 0.4-0.5

**Detected Vehicle Classes**:
```
0: car
1: motorcycle
2: bus
3: truck
4: bicycle
5: person (pedestrian)
```

**Model Architecture**:
- Backbone: CSPDarknet
- Neck: PANet
- Head: Detect head
- Training: Trained on COCO dataset (80 classes)

### 4. ByteTrack Multi-Object Tracking

ByteTrack provides robust tracking without relying on appearance features:

**Key Concepts**:
- **Track State**: Tracked, Lost, Removed
- **Track Age**: Number of frames since track created
- **Track Confidence**: Detection confidence of associated boxes

**Tracking Algorithm**:

1. **Detection Association**
   - Match high-confidence detections to existing tracks
   - Use Kalman filter for motion prediction
   - Use IoU (Intersection over Union) for matching cost

2. **Unmatched Detection Handling**
   - Match low-confidence detections to existing tracks
   - Initialize new tracks for unmatched detections
   - Smooth track transitions

3. **Track Management**
   - Keep tracks alive if not detected for N frames (default: 30)
   - Remove tracks if lost for extended period (default: 60 frames)
   - Assign stable IDs to persistent tracks

**Configuration** (in vision_engine/config.py):
```python
TRACK_BUFFER = 30           # Frames to keep lost tracks
MATCH_THRESHOLD = 0.5       # IoU threshold for matching
MIN_TRACK_LEN = 3           # Minimum frames to establish track
```

### 5. Metric Computation

#### A. Line Crossing Detection

Detects when vehicles cross a predefined line in the video frame.

**Setup**:
1. Define line coordinates in frame (x1, y1, x2, y2)
2. Track vehicle center points across frames
3. Detect crossing events

**Implementation**:
```python
def count_line_crossings(tracks, line_segment, prev_positions):
    crossings = 0
    for track in tracks:
        current_pos = track.center
        prev_pos = prev_positions.get(track.track_id)

        if prev_pos and line_segment.is_crossed(prev_pos, current_pos):
            crossings += 1

    return crossings
```

**Directions**:
- Directional counting (crossing left-to-right vs right-to-left)
- Aggregate count (total crossings, both directions)

**Use Cases**:
- Vehicle count per lane
- Traffic flow direction
- Lane utilization analysis

#### B. Zone Occupancy Analysis

Measures the percentage of frame area occupied by vehicles.

**Implementation**:
```python
def compute_zone_occupancy(detection_boxes, frame_height, frame_width):
    total_vehicle_pixels = 0

    for box in detection_boxes:
        x1, y1, x2, y2 = box
        vehicle_area = (x2 - x1) * (y2 - y1)
        total_vehicle_pixels += vehicle_area

    frame_area = frame_height * frame_width
    occupancy = total_vehicle_pixels / frame_area

    return min(occupancy, 1.0)  # Cap at 100%
```

**Interpretation**:
- 0.0-0.2: Light traffic
- 0.2-0.5: Moderate traffic
- 0.5-0.8: Heavy traffic
- 0.8-1.0: Congested

#### C. Vehicle Classification

Categorizes detected vehicles by type.

**Classes**:
- **Car**: Standard passenger vehicles
- **Motorcycle**: Two-wheeled vehicles
- **Bus**: Large public transport vehicles
- **Truck**: Heavy commercial vehicles
- **Bicycle**: Two-wheeled cycles
- **Person**: Pedestrians (if in model)

**Output**:
```json
{
  "classifications": {
    "car": 28,
    "truck": 10,
    "motorcycle": 4,
    "bus": 2
  }
}
```

#### D. Speed Estimation (Optional)

Estimates vehicle speed based on pixel displacement and calibration.

**Requirements**:
- Know distance between two reference points in frame (meters)
- Know frame rate (fps)
- Ground truth calibration

**Calculation**:
```python
def estimate_speed(pixel_distance, real_distance, fps):
    # pixels per meter
    pixels_per_meter = pixel_distance / real_distance

    # meters per frame
    meters_per_frame = 1 / pixels_per_meter

    # meters per second
    meters_per_second = meters_per_frame * fps

    # km/h
    speed_kmh = meters_per_second * 3.6

    return speed_kmh
```

**Limitations**:
- Requires camera calibration
- Affected by camera angle and perspective
- Less accurate for vehicles moving perpendicular to camera
- Skipped by default in MVP (future enhancement)

### 6. Metric Aggregation

Metrics are aggregated over time windows for periodic reporting.

**Aggregation Window**:
- Default: 5 seconds
- Configurable: 1-60 seconds

**Aggregation Process**:
```python
def aggregate_metrics(frame_metrics, window_size=5):
    aggregated = {
        'timestamp': current_timestamp,
        'vehicle_count': max(frame_metrics['vehicle_count']),
        'line_crossings': sum(frame_metrics['line_crossings']),
        'zone_occupancy': mean(frame_metrics['zone_occupancy']),
        'classifications': aggregate_classifications(frame_metrics)
    }
    return aggregated
```

**Statistics Computed**:
- **Line Crossings**: Sum over window
- **Vehicle Count**: Maximum over window
- **Zone Occupancy**: Average over window
- **Classifications**: Sum of each class over window

### 7. HTTP Publishing

Aggregated metrics are published to Backend API via HTTP.

**Endpoint**:
```
POST /api/ingest/events
```

**Headers**:
```
Content-Type: application/json
X-API-Key: <vision-api-key>
```

**Payload (current implementation)**:
```json
{
  "events": [
    {
      "camera_id": "550e8400-e29b-41d4-a716-446655440002",
      "timestamp": "2026-04-11T10:30:45Z",
      "period_seconds": 300,
      "counts": {
        "car": 28,
        "bus": 3,
        "truck": 10,
        "motorcycle": 4,
        "person": 12
      },
      "avg_occupancy": 0.45,
      "congestion_level": "moderate"
    }
  ]
}
```

**Error Handling**:
- Retry with exponential backoff on failure
- Queue events locally if backend unavailable
- Publish queued events when connection restored

## Configuration

### Environment Variables

```bash
# Model Configuration
YOLO_MODEL=yolov8n.pt          # Model size
YOLO_CONFIDENCE=0.5            # Detection confidence
YOLO_IOU=0.45                  # NMS threshold

# Camera Configuration
# In production, camera_id values are UUIDs from backend /api/cameras/
VISION_CAMERA_NAME=Demo Camera # Display name
VISION_SOURCE=rtsp://...       # Video source
VISION_FPS=30                  # Target frames per second

# Frame Configuration
VISION_FRAME_WIDTH=1280        # Target frame width
VISION_FRAME_HEIGHT=720        # Target frame height
VISION_BATCH_SIZE=1            # Batch size for inference

# Hardware Configuration
VISION_USE_GPU=true            # Enable GPU inference
VISION_GPU_DEVICE=0            # GPU device index

# Backend Configuration
VISION_BACKEND_URL=http://backend-api:8000
VISION_API_KEY=your-api-key
VISION_PUBLISH_INTERVAL=5      # Aggregation window (seconds)
```

### Configuration File (config.py)

```python
# Tracking
TRACK_BUFFER = 30              # Frames to keep lost tracks
MATCH_THRESHOLD = 0.5          # IoU threshold for matching
MIN_TRACK_LEN = 3              # Min frames to establish track

# Detection
CONFIDENCE_THRESHOLD = 0.5     # Min confidence for detection
NMS_THRESHOLD = 0.45           # NMS suppression threshold

# Processing
FRAME_BUFFER_SIZE = 100        # Max frames to buffer
PUBLISH_BATCH_SIZE = 10        # Events to batch before publishing
PUBLISH_INTERVAL = 5           # Seconds between publish attempts
```

## Performance Optimization

### GPU Acceleration

Enable CUDA for faster inference:

```bash
# Check GPU availability
nvidia-smi

# Enable GPU in .env
VISION_USE_GPU=true
```

**Speed Improvements**:
- nano model: ~7x faster (CPU: ~100ms → GPU: ~15ms)
- small model: ~7x faster
- Performance depends on GPU model

### Model Selection

Choose based on hardware and requirements:

| Requirement | Model |
|-------------|-------|
| CPU only, real-time | nano |
| CPU, accuracy important | small |
| GPU available | medium/large |
| High accuracy | xlarge |

### Frame Rate Optimization

Reduce FPS for higher throughput:

```bash
VISION_FPS=15  # Instead of 30
```

**Trade-offs**:
- Lower FPS: Faster processing, less granular metrics
- Higher FPS: More granular metrics, higher computational load

### Batch Processing

Process multiple frames at once:

```bash
VISION_BATCH_SIZE=4  # Process 4 frames per inference
```

**Limitations**:
- Increases latency
- Better GPU utilization
- Currently set to 1 for real-time streaming

## Troubleshooting

### Low FPS / High Latency

1. **Reduce frame resolution**:
   ```bash
   VISION_FRAME_WIDTH=640
   VISION_FRAME_HEIGHT=480
   ```

2. **Use smaller YOLO model**:
   ```bash
   YOLO_MODEL=yolov8n.pt
   ```

3. **Enable GPU acceleration**:
   ```bash
   VISION_USE_GPU=true
   ```

4. **Reduce FPS**:
   ```bash
   VISION_FPS=15
   ```

### High False Positives

1. **Increase confidence threshold**:
   ```bash
   YOLO_CONFIDENCE=0.6
   ```

2. **Use larger, more accurate model**:
   ```bash
   YOLO_MODEL=yolov8s.pt
   ```

### Camera Connection Issues

1. **Check RTSP URL**:
   ```bash
   ffmpeg -rtsp_transport tcp -i rtsp://camera-ip:554/stream -t 5 output.mp4
   ```

2. **Verify network connectivity**:
   ```bash
   ping camera-ip
   ```

3. **Check firewall**:
   ```bash
   sudo ufw allow 554/tcp
   ```

### Backend Connection Issues

1. **Verify backend is running**:
   ```bash
   curl http://backend-api:8000/api/health
   ```

2. **Check API key**:
   ```bash
   VISION_API_KEY=correct-key
   ```

3. **Review vision engine logs**:
   ```bash
   docker-compose logs vision-engine
   ```

## Testing & Debugging

### Local Testing

```bash
# Run vision engine locally
cd vision-engine
python -m app.main

# Process demo video
VISION_SOURCE=samples/videos/demo.mp4 python -m app.main

# Log detection results
VISION_DEBUG=true python -m app.main
```

### Demo mode and auth note

- Demo mode (`VISION_DEMO_MODE=true`) publishes events with `X-API-Key` to `/api/ingest/events`.
- Since backend business routes are JWT-protected, automatic demo seeding through unauthenticated
  `POST /api/sites` and `POST /api/cameras` may be rejected (`401`).
- Recommended flow:
  1. Start stack with `docker compose up -d`
  2. Seed backend data with `./scripts/seed-demo.sh`
  3. Start/restart vision demo pipeline

### Unit Tests

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=vision_engine tests/
```

### Inference Benchmarking

```python
# benchmark.py
import time
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.predict(source='test_frame.jpg', device=0)
print(f"Inference time: {results.speed['inference']}ms")
```

## Future Enhancements

### Phase 1.1
- Speed estimation with camera calibration
- Direction-aware line crossing counting
- Zone-based occupancy heatmaps

### Phase 1.2
- Accident/collision detection
- Violation detection (red light, wrong direction)
- License plate recognition (optional)

### Phase 2.0
- Multi-camera tracking (cross-camera vehicle linking)
- Anomaly detection (unusual traffic patterns)
- Predictive congestion modeling

### Phase 3.0
- Person re-identification for crowd analysis
- Vehicle color/type classification enhancement
- Real-time alert generation based on patterns

---

**Document Version**: 1.0.0
**Last Updated**: 2026-04-11
