# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
Image Preprocessing with OpenCV

Prepares images for OCR:
- Noise removal
- Deskewing
- Perspective correction
- Contrast enhancement
- Image cropping
- Rotation detection
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    logger.warning("OpenCV not available. Image preprocessing disabled.")


class ImageProcessor:
    """Preprocess images for OCR using OpenCV"""
    
    def __init__(self):
        """Initialize image processor"""
        if not HAS_OPENCV:
            raise RuntimeError("OpenCV is not installed. Cannot initialize ImageProcessor.")
    
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """
        Load image from file
        
        Args:
            image_path: Path to image file
        
        Returns:
            Image as numpy array (BGR format) or None if failed
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                logger.warning(f"Could not load image: {image_path}")
                return None
            return img
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str) -> bool:
        """Save processed image to file"""
        try:
            cv2.imwrite(str(output_path), image)
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False
    
    @staticmethod
    def resize_image(image: np.ndarray, width: Optional[int] = None, 
                     height: Optional[int] = None) -> np.ndarray:
        """
        Resize image maintaining aspect ratio
        
        Args:
            image: Input image
            width: Target width (if None, maintain aspect ratio)
            height: Target height (if None, maintain aspect ratio)
        
        Returns:
            Resized image
        """
        h, w = image.shape[:2]
        
        if width is None and height is None:
            return image
        
        if width is None:
            ratio = height / h
            width = int(w * ratio)
        elif height is None:
            ratio = width / w
            height = int(h * ratio)
        
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def remove_noise(image: np.ndarray) -> np.ndarray:
        """Remove noise from image using bilateral filter"""
        return cv2.bilateralFilter(image, 9, 75, 75)
    
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
        gray = ImageProcessor.convert_to_grayscale(image)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)
    
    @staticmethod
    def detect_rotation_angle(image: np.ndarray) -> float:
        """
        Detect rotation angle of document
        
        Returns:
            Rotation angle in degrees (-45 to 45)
        """
        try:
            gray = ImageProcessor.convert_to_grayscale(image)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
            
            if lines is None or len(lines) == 0:
                return 0.0
            
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = (theta * 180 / np.pi) - 90
                angles.append(angle)
            
            # Return median angle
            return float(np.median(angles)) if angles else 0.0
        except Exception as e:
            logger.warning(f"Rotation detection failed: {e}")
            return 0.0
    
    @staticmethod
    def deskew_image(image: np.ndarray, angle: Optional[float] = None) -> np.ndarray:
        """
        Deskew image by rotating to horizontal
        
        Args:
            image: Input image
            angle: Rotation angle in degrees (auto-detect if None)
        
        Returns:
            Deskewed image
        """
        if angle is None:
            angle = ImageProcessor.detect_rotation_angle(image)
        
        if abs(angle) < 0.5:
            return image
        
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Adjust bounding box
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]
        
        return cv2.warpAffine(image, rotation_matrix, (new_w, new_h),
                             borderMode=cv2.BORDER_REPLICATE)
    
    @staticmethod
    def perspective_correction(image: np.ndarray) -> np.ndarray:
        """
        Attempt perspective correction for document
        
        Uses edge detection to find document corners
        """
        try:
            gray = ImageProcessor.convert_to_grayscale(image)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return image
            
            # Find largest contour (likely the document)
            largest_contour = max(contours, key=cv2.contourArea)
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            if len(approx) != 4:
                return image
            
            # Sort points for perspective transform
            pts = approx.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            # Calculate output dimensions
            (tl, tr, br, bl) = rect
            width_a = np.linalg.norm(br - bl)
            width_b = np.linalg.norm(tr - tl)
            max_width = max(int(width_a), int(width_b))
            
            height_a = np.linalg.norm(tr - br)
            height_b = np.linalg.norm(tl - bl)
            max_height = max(int(height_a), int(height_b))
            
            dst = np.array([
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1]
            ], dtype="float32")
            
            # Apply perspective transform
            matrix = cv2.getPerspectiveTransform(rect, dst)
            return cv2.warpPerspective(image, matrix, (max_width, max_height))
        
        except Exception as e:
            logger.warning(f"Perspective correction failed: {e}")
            return image
    
    @staticmethod
    def auto_preprocess(image: np.ndarray) -> np.ndarray:
        """
        Automatically preprocess image for OCR
        
        Pipeline:
        1. Resize if too large
        2. Denoise
        3. Deskew
        4. Perspective correction
        5. Enhance contrast
        """
        # Resize if too large (max 2000px on longest side)
        h, w = image.shape[:2]
        if max(h, w) > 2000:
            image = ImageProcessor.resize_image(image, width=2000)
        
        # Denoise
        image = ImageProcessor.remove_noise(image)
        
        # Deskew
        image = ImageProcessor.deskew_image(image)
        
        # Perspective correction
        image = ImageProcessor.perspective_correction(image)
        
        # Enhance contrast
        image = ImageProcessor.enhance_contrast(image)
        
        return image
    
    @staticmethod
    def crop_to_content(image: np.ndarray) -> np.ndarray:
        """Crop image to remove borders"""
        gray = ImageProcessor.convert_to_grayscale(image)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image
        
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        return image[y:y+h, x:x+w]
