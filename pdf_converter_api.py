"""
PDF Converter API
Converts images (PNG, JPG, JPEG, etc.) to PDF files.
Provides both REST API endpoints and direct function calls.
Authors: Kai-Hsiang Chuang
Date: 02-11-2025
"""

import os
import logging
from typing import List, Optional # FOr type hinting
from pydantic import BaseModel, Field # For data validation and data parsing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ConversionRequest(BaseModel):
    """Request model for directory-based conversion"""
    input_dir: str = Field(..., description = "Directory containing images")
    output_pdf_path: str = Field(..., description = "Output PDF file path")
    image_format: Optional[List[str]] = Field(
        default=None,
        description="List of image formats to include (e.g., ['png', 'jpg'])"
    )