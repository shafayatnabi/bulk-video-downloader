# Bulk Video Downloader

A PyQt6-based desktop application for downloading multiple videos from web pages with an intuitive GUI interface.

## Features

- **Modern PyQt6 GUI** - Clean, professional interface
- **URL Input** - Paste website URLs to crawl for videos
- **Video Detection** - Automatically finds video files on web pages
- **Bulk Download** - Download multiple videos simultaneously
- **Overall Progress Tracking** - Monitor overall download progress
- **Best Quality Downloads** - Always downloads the best available quality
- **Concurrent Downloads** - Configurable concurrent download limits
- **Download Management** - Start, pause, and stop downloads

## Screenshots

*Screenshots will be added once the application is fully functional*

## Installation

### Prerequisites
- Python 3.8 or higher
- macOS, Linux, or Windows

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shafayatnabi/bulk-video-downloader.git
   cd bulk-video-downloader
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

1. **Run the application:**
   ```bash
   # Option 1: Use the run script
   python run.py
   
   # Option 2: Run directly
   source venv/bin/activate
   python src/main.py
   
   # Option 3: Install and run as package
   pip install -e .
   bulk-video-downloader-gui
   ```

2. **Enter a website URL** in the URL input field
3. **Click "Crawl for Videos"** to detect video files
4. **Select videos** from the detected list
5. **Configure download settings** (folder and concurrent downloads)
6. **Click "Start Download"** to begin downloading

### Features

- **URL Input**: Paste any website URL to scan for videos
- **Download Settings**: Configure download folder and concurrent download limit
- **Video Selection**: Multi-select videos from the detected list
- **Progress Monitoring**: Track overall download progress
- **Download Controls**: Start, pause, and stop downloads

## Development

### Project Structure
```
bulk_video_downloader/
├── src/                    # Source code
│   ├── main.py            # Application entry point
│   ├── gui/               # GUI components
│   │   ├── main_window.py # Main application window
│   │   └── __init__.py
│   ├── core/              # Core functionality
│   ├── utils/             # Utility functions
│   └── __init__.py
├── config/                 # Configuration files
├── test/                   # Test files
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
└── run.py                 # Quick run script
```

### Running Tests
```bash
source venv/bin/activate
pytest
```

### Code Formatting
```bash
source venv/bin/activate
black src/
flake8 src/
```

## Dependencies

- **PyQt6** - Modern Qt framework for GUI
- **requests** - HTTP library for web requests
- **beautifulsoup4** - HTML parsing for video detection
- **yt-dlp** - Video downloading engine
- **aiohttp** - Async HTTP for concurrent downloads
- **PyYAML** - Configuration file handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Shafayat Nabi Chowdhury**
- Email: snabi3@gmail.com
- GitHub: [@shafayatnabi](https://github.com/shafayatnabi)

## Roadmap

- [ ] Video crawling implementation
- [ ] Download manager with progress tracking
- [ ] Support for multiple video platforms
- [ ] Batch download scheduling
- [ ] Download resume capability
- [ ] Video format conversion
- [ ] Subtitle download support
- [ ] Advanced filtering options

## Issues

If you encounter any issues, please:
1. Check the troubleshooting section below
2. Search existing issues
3. Create a new issue with detailed information

## Troubleshooting

### Common Issues

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**PyQt6 not found:**
- Install PyQt6: `pip install PyQt6`
- Alternative: Use PySide6: `pip install PySide6`

**Permission errors:**
- Make run script executable: `chmod +x run.py`

**Dependencies conflicts:**
- Use virtual environment: `python3 -m venv venv`
- Activate and install: `source venv/bin/activate && pip install -r requirements.txt`
