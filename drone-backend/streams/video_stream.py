"""
Video stream handling for webcam, RTSP, or file sources
"""
import cv2
import threading
import time
import logging
from typing import Optional, Callable
from collections import deque

from config import STREAM_FPS, MAX_STREAM_RESOLUTION
from utils.image_utils import resize_maintain_aspect

logger = logging.getLogger(__name__)


class VideoStream:
    """Handles video capture from various sources"""
    
    def __init__(self, source: int = 0):
        """
        Initialize video stream
        
        Args:
            source: Camera index (0 for webcam) or RTSP URL or video file path
        """
        self.source = source
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.frame_queue = deque(maxlen=3)  # Keep last 3 frames
        
    def start(self):
        """Start video capture"""
        logger.info(f"Starting video stream from source: {self.source}")
        
        # Open capture
        if isinstance(self.source, int):
            self.cap = cv2.VideoCapture(self.source)
        else:
            self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {self.source}")
        
        # Set properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, MAX_STREAM_RESOLUTION[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, MAX_STREAM_RESOLUTION[1])
        self.cap.set(cv2.CAP_PROP_FPS, STREAM_FPS)
        
        self.running = True
        
        # Start frame reading thread
        self.thread = threading.Thread(target=self._read_frames, daemon=True)
        self.thread.start()
        
        logger.info("Video stream started successfully")
    
    def _read_frames(self):
        """Continuously read frames from camera"""
        while self.running:
            ret, frame = self.cap.read()
            
            if ret:
                # Resize if needed
                frame = resize_maintain_aspect(frame, MAX_STREAM_RESOLUTION)
                
                with self.lock:
                    self.frame = frame
                    self.frame_queue.append(frame.copy())
            else:
                logger.warning("Failed to read frame")
                time.sleep(0.01)
    
    def read(self) -> Optional[np.ndarray]:
        """Get latest frame"""
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
        return None
    
    def get_recent_frames(self, count: int = 3) -> list:
        """Get recent frames from queue"""
        with self.lock:
            return [f.copy() for f in list(self.frame_queue)[-count:]]
    
    def stop(self):
        """Stop video capture"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
        logger.info("Video stream stopped")
    
    def __del__(self):
        self.stop()