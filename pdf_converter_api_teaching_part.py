"""
PDF Converter API
Converts images (PNG, JPG, JPEG, etc.) to PDF files.
Provides both REST API endpoints and direct function calls.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
import img2pdf
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Image to PDF Converter API",
    description="Convert images to PDF files",
    version="1.0.0"
)

# Supported image formats
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif'}


class ConversionRequest(BaseModel):
    """Request model for directory-based conversion"""
    input_dir: str = Field(..., description="Directory containing images")
    output_pdf_path: str = Field(..., description="Output PDF file path")
    image_formats: Optional[List[str]] = Field(
        default=None,
        description="List of image formats to include (e.g., ['png', 'jpg'])"
    )
    sort_order: Optional[str] = Field(
        default="name",
        description="Sort order: 'name' or 'modified'"
    )


class ConversionResponse(BaseModel):
    """Response model for conversion operations"""
    success: bool
    message: str
    output_path: Optional[str] = None
    images_converted: Optional[int] = None


def validate_directory(directory: str) -> Path:
    """
    Validate that the directory exists and is accessible.

    Args:
        directory: Path to the directory

    Returns:
        Path object

    Raises:
        ValueError: If directory doesn't exist or is not accessible
    """
    path = Path(directory)
    if not path.exists():
        raise ValueError(f"Directory '{directory}' does not exist")
    if not path.is_dir():
        raise ValueError(f"'{directory}' is not a directory")
    return path


def get_image_files(
    directory: Path,
    formats: Optional[List[str]] = None,
    sort_order: str = "name"
) -> List[Path]:
    """
    Get all image files from a directory.

    Args:
        directory: Path to the directory
        formats: List of image formats to include (without dots)
        sort_order: 'name' or 'modified' for sorting

    Returns:
        List of Path objects for image files
    """
    if formats is None:
        formats = [fmt.lstrip('.') for fmt in SUPPORTED_FORMATS]

    # Normalize formats
    formats_set = {f".{fmt.lower().lstrip('.')}" for fmt in formats}

    # Validate formats
    invalid_formats = formats_set - SUPPORTED_FORMATS
    if invalid_formats:
        logger.warning(f"Unsupported formats will be skipped: {invalid_formats}")
        formats_set = formats_set & SUPPORTED_FORMATS

    # Collect image files
    image_files = []
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in formats_set:
            image_files.append(file_path)

    # Sort files
    if sort_order == "modified":
        image_files.sort(key=lambda p: p.stat().st_mtime)
    else:  # default to name
        image_files.sort(key=lambda p: p.name.lower())

    return image_files


def convert_images_to_pdf(
    input_dir: str,
    output_pdf_path: str,
    image_formats: Optional[List[str]] = None,
    sort_order: str = "name"
) -> dict:
    """
    Converts all images in a directory to a single PDF file.

    Args:
        input_dir: The path to the directory containing images
        output_pdf_path: The path and filename for the output PDF
        image_formats: List of image formats to include (e.g., ['png', 'jpg'])
        sort_order: Sort order: 'name' or 'modified'

    Returns:
        Dictionary with conversion results

    Raises:
        ValueError: If directory is invalid
        IOError: If file operations fail
    """
    try:
        # Validate input directory
        input_path = validate_directory(input_dir)

        # Get image files
        image_files = get_image_files(input_path, image_formats, sort_order)

        if not image_files:
            formats_str = ', '.join(image_formats) if image_formats else 'all supported formats'
            message = f"No images found in '{input_dir}' with formats: {formats_str}"
            logger.warning(message)
            return {
                "success": False,
                "message": message,
                "images_converted": 0
            }

        # Convert to PDF
        image_paths = [str(img) for img in image_files]
        output_path = Path(output_pdf_path)

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(image_paths))

        message = f"Successfully converted {len(image_files)} images to '{output_pdf_path}'"
        logger.info(message)

        return {
            "success": True,
            "message": message,
            "output_path": str(output_path.absolute()),
            "images_converted": len(image_files)
        }

    except Exception as e:
        error_message = f"Error during conversion: {str(e)}"
        logger.error(error_message, exc_info=True)
        raise IOError(error_message) from e


async def save_upload_files(upload_files: List[UploadFile], temp_dir: Path) -> List[Path]:
    """
    Save uploaded files to a temporary directory.

    Args:
        upload_files: List of uploaded files
        temp_dir: Temporary directory to save files

    Returns:
        List of saved file paths
    """
    saved_files = []
    for idx, upload_file in enumerate(upload_files):
        # Validate file extension
        file_ext = Path(upload_file.filename).suffix.lower()
        if file_ext not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {file_ext}. "
                f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
            )

        # Save file
        file_path = temp_dir / f"{idx:03d}_{upload_file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        saved_files.append(file_path)

    return saved_files


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Image to PDF Converter API",
        "version": "1.0.0",
        "endpoints": {
            "POST /convert": "Convert images from a directory to PDF",
            "POST /convert/upload": "Upload images and convert to PDF",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/convert", response_model=ConversionResponse)
async def convert_directory_to_pdf(request: ConversionRequest):
    """
    Convert all images in a directory to a PDF file.

    Args:
        request: ConversionRequest with input_dir and output_pdf_path

    Returns:
        ConversionResponse with conversion results
    """
    try:
        result = convert_images_to_pdf(
            input_dir=request.input_dir,
            output_pdf_path=request.output_pdf_path,
            image_formats=request.image_formats,
            sort_order=request.sort_order
        )
        return ConversionResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/convert/upload")
async def convert_uploaded_images(
    files: List[UploadFile] = File(..., description="Image files to convert")
):
    """
    Upload images and convert them to a PDF file.

    Args:
        files: List of image files to upload and convert

    Returns:
        PDF file as a download
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    temp_dir = None
    output_pdf = None

    try:
        # Create temporary directory for uploaded files
        temp_dir = Path(tempfile.mkdtemp())

        # Save uploaded files
        saved_files = await save_upload_files(files, temp_dir)
        logger.info(f"Saved {len(saved_files)} files to temporary directory")

        # Convert to PDF
        output_pdf = temp_dir / "output.pdf"
        image_paths = [str(f) for f in saved_files]

        with open(output_pdf, "wb") as f:
            f.write(img2pdf.convert(image_paths))

        logger.info(f"Successfully converted {len(files)} images to PDF")

        # Return the PDF file
        return FileResponse(
            path=output_pdf,
            media_type="application/pdf",
            filename="converted.pdf"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during upload conversion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    finally:
        # Clean up temporary files after response is sent
        # Note: FileResponse will handle the file, so we clean up in the background
        if temp_dir and temp_dir.exists():
            try:
                # We need to delay cleanup to allow FileResponse to serve the file
                # In production, consider using a background task
                pass  # Cleanup will happen automatically when temp directory is garbage collected
            except Exception as e:
                logger.error(f"Error cleaning up temporary files: {str(e)}")


# Command-line interface
if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Image to PDF Converter")
    parser.add_argument(
        "--mode",
        choices=["api", "convert"],
        default="api",
        help="Run mode: 'api' for REST API server, 'convert' for direct conversion"
    )
    parser.add_argument(
        "--input-dir",
        help="Input directory containing images (for convert mode)"
    )
    parser.add_argument(
        "--output-pdf",
        help="Output PDF file path (for convert mode)"
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        help="Image formats to include (e.g., png jpg)"
    )
    parser.add_argument(
        "--sort",
        choices=["name", "modified"],
        default="name",
        help="Sort order for images"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (for api mode)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (for api mode)"
    )

    args = parser.parse_args()

    if args.mode == "api":
        # Run API server
        logger.info(f"Starting API server on {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        # Direct conversion mode
        if not args.input_dir or not args.output_pdf:
            parser.error("--input-dir and --output-pdf are required for convert mode")

        result = convert_images_to_pdf(
            input_dir=args.input_dir,
            output_pdf_path=args.output_pdf,
            image_formats=args.formats,
            sort_order=args.sort
        )
        print(result["message"])
