# Image to PDF Converter API

A comprehensive Python application that converts images to PDF files, with both REST API and command-line interfaces.

## Features

- Convert multiple image formats (PNG, JPG, JPEG, BMP, TIFF, GIF) to PDF
- REST API with FastAPI
- File upload support
- Directory-based conversion
- Configurable sort order (by name or modification date)
- Comprehensive error handling and logging
- Input validation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### API Mode (REST API Server)

Start the API server:
```bash
python pdf_converter_api.py --mode api --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

#### API Endpoints

**1. Convert from Directory**
```bash
POST /convert
Content-Type: application/json

{
  "input_dir": "/path/to/images",
  "output_pdf_path": "/path/to/output.pdf",
  "image_formats": ["png", "jpg"],  # optional
  "sort_order": "name"  # or "modified"
}
```

**2. Upload and Convert**
```bash
POST /convert/upload
Content-Type: multipart/form-data

files: [image1.png, image2.jpg, ...]
```

**3. Health Check**
```bash
GET /health
```

#### Example API Usage with cURL

Convert from directory:
```bash
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "input_dir": ".",
    "output_pdf_path": "output.pdf",
    "image_formats": ["png", "jpg"]
  }'
```

Upload and convert:
```bash
curl -X POST "http://localhost:8000/convert/upload" \
  -F "files=@image1.png" \
  -F "files=@image2.jpg" \
  --output converted.pdf
```

#### Example API Usage with Python

```python
import requests

# Convert from directory
response = requests.post(
    "http://localhost:8000/convert",
    json={
        "input_dir": "./images",
        "output_pdf_path": "./output.pdf",
        "image_formats": ["png", "jpg"],
        "sort_order": "name"
    }
)
print(response.json())

# Upload and convert
files = [
    ('files', open('image1.png', 'rb')),
    ('files', open('image2.jpg', 'rb'))
]
response = requests.post(
    "http://localhost:8000/convert/upload",
    files=files
)
with open('result.pdf', 'wb') as f:
    f.write(response.content)
```

### Direct Conversion Mode

Convert images from a directory directly:
```bash
python pdf_converter_api.py \
  --mode convert \
  --input-dir ./images \
  --output-pdf output.pdf \
  --formats png jpg \
  --sort name
```

### Using as a Python Module

```python
from pdf_converter_api import convert_images_to_pdf

# Convert all images in a directory
result = convert_images_to_pdf(
    input_dir="./images",
    output_pdf_path="output.pdf",
    image_formats=["png", "jpg"],
    sort_order="name"
)

print(result)
# {
#   'success': True,
#   'message': 'Successfully converted 5 images to output.pdf',
#   'output_path': '/absolute/path/to/output.pdf',
#   'images_converted': 5
# }
```

## Configuration Options

- **image_formats**: List of image formats to include (default: all supported formats)
- **sort_order**:
  - `name`: Sort by filename alphabetically (default)
  - `modified`: Sort by file modification time

## Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- GIF (.gif)

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error

All errors include detailed error messages in the response.

## Logging

The application uses Python's logging module. Logs include:
- Conversion operations
- File operations
- Errors and warnings

## Development

To run in development mode with auto-reload:
```bash
uvicorn pdf_converter_api:app --reload --host 0.0.0.0 --port 8000
```

## License

MIT License
