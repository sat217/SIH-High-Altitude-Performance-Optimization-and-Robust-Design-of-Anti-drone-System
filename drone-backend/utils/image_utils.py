"""
Image processing utilities for glare/whiteout detection and thermal conversion
"""
import cv2
import numpy as np
from typing import Tuple


def detect_glare(image: np.ndarray, threshold: int = 200) -> bool:
    """
    Detect if image has significant glare/bright spots
    
    Args:
        image: Input BGR image
        threshold: Pixel intensity threshold (0-255)
    
    Returns:
        True if glare detected, False otherwise
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate percentage of pixels above threshold
    bright_pixels = np.sum(gray > threshold)
    total_pixels = gray.size
    bright_percentage = (bright_pixels / total_pixels) * 100
    
    # If more than 30% of pixels are very bright, it's likely glare
    return bright_percentage > 30


def detect_whiteout(image: np.ndarray, threshold: int = 240) -> bool:
    """
    Detect if image is washed out (whiteout condition)
    
    Args:
        image: Input BGR image
        threshold: Pixel intensity threshold for whiteout
    
    Returns:
        True if whiteout detected, False otherwise
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate mean and std deviation
    mean_intensity = np.mean(gray)
    std_intensity = np.std(gray)
    
    # Whiteout: high mean intensity AND low variance (everything is bright)
    return mean_intensity > threshold and std_intensity < 30


def convert_to_thermal(image: np.ndarray) -> np.ndarray:
    """
    Simulate thermal imaging by converting RGB to false-color thermal representation
    
    Args:
        image: Input BGR image
    
    Returns:
        Thermal-like visualization in BGR format
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply histogram equalization for better contrast
    gray_eq = cv2.equalizeHist(gray)
    
    # Apply color map to simulate thermal imaging
    # COLORMAP_JET gives blue-cold, red-hot appearance
    thermal = cv2.applyColorMap(gray_eq, cv2.COLORMAP_JET)
    
    return thermal


def enhance_image(image: np.ndarray) -> np.ndarray:
    """
    Enhance image quality for better detection
    
    Args:
        image: Input BGR image
    
    Returns:
        Enhanced image
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    # Merge channels back
    merged = cv2.merge((cl, a, b))
    
    # Convert back to BGR
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    
    return enhanced


def resize_maintain_aspect(image: np.ndarray, max_size: Tuple[int, int] = (1280, 720)) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio
    
    Args:
        image: Input image
        max_size: Maximum dimensions (width, height)
    
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    max_w, max_h = max_size
    
    # Calculate scaling factor
    scale = min(max_w / w, max_h / h)
    
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized
    
    return image