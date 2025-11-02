"""
PDF Converter API
Converts images (PNG, JPG, JPEG, etc.) to PDF files.
Provides both REST API endpoints and direct function calls.
Authors: Kai-Hsiang Chuang
Date: 02-11-2025
"""

import os
from pydantic import BaseModel, Field # For data validation and data parsing


class ConversionRequest(BaseModel):
    """Request model for directory-based conversion"""
    input_dir: str = Field(..., description = "Directory containing images")
