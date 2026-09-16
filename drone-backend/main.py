"""
SKY SENTINEL Backend - Main Application
FastAPI server with YOLOv8 detection, thermal processing, and WebSocket streaming
"""
import asyncio
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

# Import our modules
from config import WS_HOST, WS_PORT
from detectors.yolo_detector import DroneDetector
from detectors.thermal_processor import ThermalProcessor
from streams.video_stream import VideoStream
from streams.websocket_manager import WebSocketManager
from utils.alert_system import AlertSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
detector = None
thermal_processor = None
video_stream = None
ws_manager = None
alert_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global detector, thermal_processor, video_stream, ws_manager, alert_system
    
    # Startup
    logger.info("🚀 Starting SKY SENTINEL Backend...")
    
    # Initialize components
    detector = DroneDetector()
    thermal_processor = ThermalProcessor()
    ws_manager = WebSocketManager()
    alert_system = AlertSystem(cooldown=5, max_alerts=10)
    
    # Start video stream (webcam by default)
    video_stream = VideoStream(source=0)
    video_stream.start()
    
    logger.info("✅ SKY SENTINEL Backend ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if video_stream:
        video_stream.stop()


# Create FastAPI app
app = FastAPI(
    title="SKY SENTINEL Backend",
    description="Drone Detection System with Thermal Imaging",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "system": "SKY SENTINEL Backend",
        "version": "1.0.0"
    }


@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "detector": "ready" if detector else "not initialized",
        "thermal_processor": "ready" if thermal_processor else "not initialized",
        "video_stream": "running" if video_stream and video_stream.running else "stopped",
        "websocket_connections": len(ws_manager.active_connections) if ws_manager else 0,
        "current_mode": thermal_processor.get_mode_status() if thermal_processor else None
    }


@app.post("/detect/upload")
async def detect_from_upload(file: UploadFile = File(...)):
    """Detect drones in uploaded image"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return JSONResponse(status_code=400, content={"error": "Invalid image file"})
        
        processed_image, mode = thermal_processor.process_frame(image)
        detections = detector.detect(processed_image, use_thermal=(mode == 'thermal'))
        output_image = detector.draw_detections(processed_image, detections)
        
        _, encoded = cv2.imencode('.jpg', output_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        import base64
        result_base64 = base64.b64encode(encoded).decode('utf-8')
        
        return {
            "success": True,
            "mode": mode,
            "detections": detections,
            "image": result_base64,
            "detection_count": len(detections)
        }
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time video streaming"""
    await ws_manager.connect(websocket)
    
    try:
        while True:
            frame = video_stream.read()
            
            if frame is None:
                await asyncio.sleep(0.033)
                continue
            
            # Process frame
            processed_frame, mode = thermal_processor.process_frame(frame)
            
            # Run detection
            detections = detector.detect(
                processed_frame, 
                use_thermal=(mode == 'thermal')
            )
            
            # Draw detections
            output_frame = detector.draw_detections(processed_frame, detections)
            
            # Send frame ONLY (no alerts to prevent crashes)
            await ws_manager.send_frame(
                output_frame, 
                detections=detections,
                mode=mode
            )
            
            await asyncio.sleep(0.033)
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@app.get("/alerts/recent")
async def get_recent_alerts(count: int = 10):
    """Get recent detection alerts"""
    return {"alerts": alert_system.get_recent_alerts(count)}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {WS_HOST}:{WS_PORT}")
    uvicorn.run(
        "main:app",
        host=WS_HOST,
        port=WS_PORT,
        reload=True,
        log_level="info"
    )