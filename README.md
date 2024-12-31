
# MarkItDown Converter

A web-based tool that converts various file formats to Markdown, powered by Microsoft's MarkItDown library.

## Features

- Drag-and-drop file upload
- Multiple file conversion support
- Bulk download as ZIP
- Progress tracking
- Conversion history
- Clean, modern UI

## Supported Formats

- PDF
- Microsoft Office (Word, PowerPoint, Excel)
- Images (EXIF + OCR support)
- Audio (EXIF + transcription)
- HTML
- Text formats (CSV, JSON, XML)
- ZIP files

## Getting Started

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python main.py
```

The server will start on port 8080.

## Usage

1. Open your browser and navigate to the application
2. Drag and drop files or click to select files
3. Wait for the conversion to complete
4. Download individual files or get all as ZIP
5. View conversion history below the upload area

## Tech Stack

- Python Flask
- Microsoft MarkItDown
- JavaScript (Frontend)
- CSS3 with modern animations
- JSZip for bulk downloads

## API Endpoints

- `POST /convert` - Convert multiple files
- `POST /api/convert` - Convert single file (API usage)

## Development

This project is developed on Replit, making it easy to fork and customize. Visit our Replit project to start contributing.

## Credits

- Powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
- Created by José Luis Saorín

## License

MIT License
