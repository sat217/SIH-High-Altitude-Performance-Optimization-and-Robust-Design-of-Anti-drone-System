import torch
"""
YOLOv8-based drone detection module
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Optional
import logging

from config import YOLO_MODEL_PATH, YOLO_CONFIDENCE_THRESHOLD, YOLO_IOU_THRESHOLD

logger = logging.getLogger(__name__)


class DroneDetector:
    """YOLOv8-based object detector optimized for drone detection"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLO model weights
        """
        self.model_path = model_path or YOLO_MODEL_PATH
        
        # Check if model exists
        if not self.model_path.exists():
            logger.warning(f"Model not found at {self.model_path}. Downloading YOLOv8n...")
            self._download_model()
        
        # Load YOLO model
        logger.info(f"Loading YOLO model from {self.model_path}")
        self.model = YOLO(str(self.model_path))
        
        # Set device (GPU if available, else CPU)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")
        
    def _download_model(self):
        """Download default YOLOv8n model"""
        try:
            from ultralytics import YOLO
            # This will download the model automatically
            temp_model = YOLO('yolov8n.pt')
            logger.info("YOLOv8n model downloaded successfully")
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise
    
    def detect(self, image: np.ndarray, confidence: float = None, 
               use_thermal: bool = False) -> List[Dict]:
        """
        Perform object detection on image
        
        Args:
            image: Input BGR image
            confidence: Detection confidence threshold
            use_thermal: Whether image is thermal-enhanced
        
        Returns:
            List of detections with bounding boxes and classes
        """
        conf_threshold = confidence or YOLO_CONFIDENCE_THRESHOLD
        
        try:
            # Run inference
            results = self.model(
                image,
                conf=conf_threshold,
                iou=YOLO_IOU_THRESHOLD,
                verbose=False,
                device=self.device
            )
            
            detections = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                
                if boxes is None:
                    continue
                
                # Extract boxes data
                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence_score = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    detection = {
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': confidence_score,
                        'class_id': class_id,
                        'class_name': self.model.names[class_id],
                        'is_thermal': use_thermal
                    }
                    
                    detections.append(detection)
            
            logger.debug(f"Detected {len(detections)} objects")
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw detection boxes on image
        
        Args:
            image: Input BGR image
            detections: List of detection dictionaries
        
        Returns:
            Image with drawn detections
        """
        output = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_name = det['class_name']
            
            # Choose color based on detection type
            if det.get('is_thermal', False):
                color = (0, 255, 255)  # Yellow for thermal
            else:
                color = (0, 255, 0)  # Green for normal
            
            # Draw bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 2
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, thickness
            )
            
            # Draw filled rectangle for label background
            cv2.rectangle(
                output,
                (x1, y1 - text_height - 10),
                (x1 + text_width, y1),
                color,
                cv2.FILLED
            )
            
            # Draw text
            cv2.putText(
                output,
                label,
                (x1, y1 - 5),
                font,
                font_scale,
                (0, 0, 0),
                thickness
            )
        
        return output