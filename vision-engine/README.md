# SEN TRAFIC AI - Vision Engine

Real-time traffic analysis and vehicle detection engine for Senegal/Dakar using Ultralytics YOLO and OpenCV.

## Overview

The Vision Engine is a production-ready computer vision system that:
- Detects and tracks vehicles in real-time from video streams
- Counts vehicles crossing defined counting lines
- Monitors occupancy in designated zones
- Detects stalled vehicles
- Publishes aggregated traffic metrics to the backend API
- Supports both local video files and RTSP camera streams

## Supported Classes

- Car
- Bus
- Truck
- Motorcycle
- Person

## Features

- **Real-time Detection**: Uses YOLOv8 nano for efficient inference
- **Multi-object Tracking**: ByteTrack integration for consistent object IDs
- **Line Counting**: Counts vehicles crossing horizontal counting lines
- **Zone Monitoring**: Tracks occupancy within defined polygonal zones
- **Stall Detection**: Identifies vehicles that haven't moved for extended periods
- **Traffic Aggregation**: Summarizes metrics over configurable time windows
- **Backend Publishing**: Publishes results to backend API with retry logic
- **Display Mode**: Optional real-time visualization with overlays
- **RTSP Support**: Automatic reconnection for network camera streams
- **Logging**: Comprehensive logging for debugging and monitoring

## Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Setup

1. Clone/navigate to the vision-engine directory
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download a demo video (optional) and place it in `samples/videos/demo.mp4`

5. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Configuration

All configuration is managed via environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `VISION_SOURCE` | `samples/videos/demo.mp4` | Video file path or RTSP URL |
| `VISION_CAMERA_ID` | `1` | Unique camera identifier |
| `YOLO_MODEL` | `yolov8n.pt` | YOLO model file (nano, small, medium, large, xlarge) |
| `YOLO_CONFIDENCE` | `0.35` | Detection confidence threshold (0-1) |
| `YOLO_IOU` | `0.45` | NMS IoU threshold (0-1) |
| `BACKEND_URL` | `http://localhost:8000` | Backend API base URL |
| `BACKEND_API_KEY` | `vision-engine-key` | API authentication key |
| `PUBLISH_INTERVAL` | `300` | Aggregation window in seconds |
| `LINE_Y_RATIO` | `0.6` | Counting line position (0-1, ratio of frame height) |
| `ZONE_POINTS` | `0.2,0.3,0.8,0.3,0.8,0.9,0.2,0.9` | Zone polygon as comma-separated normalized coordinates (x1,y1,x2,y2,...) |
| `DISPLAY_OUTPUT` | `false` | Show real-time visualization (requires display) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

## Usage

### Run the Engine

```bash
python -m app.main
```

The engine will:
1. Initialize the YOLO model
2. Open the video source
3. Process frames continuously
4. Publish aggregated results to the backend every `PUBLISH_INTERVAL` seconds
5. Exit gracefully on Ctrl+C or stream end

### Demo Mode

To run with a demo video:
```bash
python -m app.main
```

Ensure `samples/videos/demo.mp4` exists, or download a sample traffic video and place it there.

### RTSP Camera Stream

To use a live camera:
```bash
# Set VISION_SOURCE in .env
VISION_SOURCE=rtsp://username:password@camera-ip:554/stream
```

The engine automatically handles connection losses and attempts reconnection.

### Display Mode

To visualize detections in real-time:
```bash
# Set in .env
DISPLAY_OUTPUT=true
```

This shows:
- Bounding boxes with class names and confidence scores
- Counting line with vehicle counts
- Zone polygon with occupancy percentage
- Real-time FPS and processing info

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Individual test modules:
```bash
pytest tests/test_config.py -v
pytest tests/test_counters.py -v
pytest tests/test_zones.py -v
```

## Architecture

```
vision-engine/
├── app/
│   ├── __init__.py
│   ├── main.py          # Pipeline orchestration
│   ├── config.py        # Configuration management
│   ├── models.py        # Data models
│   ├── utils.py         # Utility functions
│   ├── detector.py      # YOLO detector wrapper
│   ├── tracker.py       # Object tracker
│   ├── stream.py        # Video stream handler
│   ├── counters.py      # Line counter & stall detector
│   ├── zones.py         # Zone monitor
│   ├── aggregator.py    # Metrics aggregation
│   └── publisher.py     # Backend API publisher
├── tests/
│   ├── test_config.py
│   ├── test_counters.py
│   └── test_zones.py
├── samples/videos/
│   └── demo-placeholder.txt
├── README.md
├── requirements.txt
└── .env.example
```

## Backend API Integration

The engine publishes results to: `{BACKEND_URL}/api/ingest/events`

### Payload Format

```json
{
  "camera_id": "1",
  "timestamp": "2024-01-15T14:30:00Z",
  "period_seconds": 300,
  "counts": {
    "car": 42,
    "bus": 8,
    "truck": 3,
    "motorcycle": 15,
    "person": 5
  },
  "avg_occupancy": 0.45,
  "congestion_level": "moderate"
}
```

### Authentication

Include the API key in the `X-API-Key` header:
```
X-API-Key: vision-engine-key
```

## Performance Tips

- **Model Size**: Use `yolov8n.pt` for 30+ fps on CPU. Use larger models if GPU available.
- **Confidence Threshold**: Higher threshold (0.5+) reduces false positives but may miss distant objects.
- **Display Mode**: Disable `DISPLAY_OUTPUT` in production for better performance.
- **Frame Skipping**: For lower-resolution analysis, process every Nth frame.
- **Resolution**: Reduce input resolution for faster processing.

## Troubleshooting

### Model not found
Download the YOLO model:
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### No detections
- Verify YOLO_CONFIDENCE is appropriate for your scene (try 0.25-0.4)
- Ensure video has sufficient lighting
- Check that video resolution is adequate

### Backend connection issues
- Verify `BACKEND_URL` is accessible
- Check API key in `.env`
- Review logs for detailed error messages

### Performance issues
- Reduce YOLO_MODEL to nano version
- Disable `DISPLAY_OUTPUT`
- Process lower-resolution video
- Check system CPU/GPU utilization

## Logging

Logs are printed to stdout and can be captured to a file:

```bash
python -m app.main 2>&1 | tee vision-engine.log
```

Set `LOG_LEVEL=DEBUG` for verbose output.

## License

Proprietary - SEN TRAFIC AI

## Support

For issues or questions, contact the development team.
