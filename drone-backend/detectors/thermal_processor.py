"""
Thermal image processing and automatic switching logic
"""
import cv2
import numpy as np
from typing import Tuple, Optional
import logging

from utils.image_utils import detect_glare, detect_whiteout, convert_to_thermal, enhance_image
from config import GLARE_DETECTION_THRESHOLD, WHITEOUT_THRESHOLD

logger = logging.getLogger(__name__)


class ThermalProcessor:
    """Handles thermal image simulation and automatic mode switching"""
    
    def __init__(self):
        self.mode = 'normal'  # 'normal' or 'thermal'
        self.last_switch_time = None
        self.switch_cooldown = 5  # seconds
        
    def should_switch_to_thermal(self, image: np.ndarray) -> bool:
        """
        Determine if conditions warrant switching to thermal mode
        
        Args:
            image: Input BGR image
        
        Returns:
            True if should switch to thermal, False otherwise
        """
        # Check for glare
        has_glare = detect_glare(image, GLARE_DETECTION_THRESHOLD)
        
        # Check for whiteout
        has_whiteout = detect_whiteout(image, WHITEOUT_THRESHOLD)
        
        # Calculate overall brightness
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Decision logic
        if has_glare or has_whiteout or mean_brightness > 220:
            logger.info(f"Switching to thermal mode - Glare: {has_glare}, Whiteout: {has_whiteout}, Brightness: {mean_brightness:.2f}")
            return True
        
        return False
    
    def process_frame(self, image: np.ndarray, force_thermal: bool = False) -> Tuple[np.ndarray, str]:
        """
        Process frame and determine appropriate mode
        
        Args:
            image: Input BGR image
            force_thermal: Force thermal mode regardless of conditions
        
        Returns:
            Tuple of (processed_image, mode_used)
        """
        if force_thermal or self.should_switch_to_thermal(image):
            # Switch to thermal mode
            processed = convert_to_thermal(image)
            self.mode = 'thermal'
            logger.debug("Using thermal mode")
        else:
            # Use normal mode with enhancement
            processed = enhance_image(image)
            self.mode = 'normal'
            logger.debug("Using normal mode")
        
        return processed, self.mode
    
    def get_mode_status(self) -> dict:
        """Get current processing mode status"""
        return {
            'mode': self.mode,
            'timestamp': self.last_switch_time
        }