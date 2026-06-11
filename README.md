# Instagram Reels Downloader

A Python tool to download Instagram Reels easily and quickly.

## Features

- ✅ Download Instagram Reels by URL or Reel ID
- ✅ Batch download multiple reels
- ✅ Save metadata (title, description, likes, comments)
- ✅ Progress tracking
- ✅ Error handling and retry logic
- ✅ Support for both public and private accounts (with authentication)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kakubagri99-code/Instagram-Reels-downloader.git
cd Instagram-Reels-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional, for authentication):
```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

## Usage

### As a Command Line Tool

Download a single reel:
```bash
python main.py --url "https://www.instagram.com/reel/ABC123DEF/"
```

Download by reel ID:
```bash
python main.py --id "ABC123DEF"
```

Download multiple reels:
```bash
python main.py --urls urls.txt
```

Specify output directory:
```bash
python main.py --url "https://www.instagram.com/reel/ABC123DEF/" --output ./downloads
```

### As a Python Module

```python
from reels_downloader import InstagramReelsDownloader

downloader = InstagramReelsDownloader()

# Download a single reel
downloader.download_reel("https://www.instagram.com/reel/ABC123DEF/")

# Download with custom output path
downloader.download_reel("ABC123DEF", output_dir="./my_downloads")
```

## Options

- `--url`: Direct Instagram reel URL
- `--id`: Instagram reel ID
- `--urls`: Text file with multiple URLs (one per line)
- `--output`: Output directory (default: `./downloads`)
- `--username`: Instagram username (for private accounts)
- `--password`: Instagram password (for private accounts)
- `--metadata`: Save metadata as JSON (default: True)
- `--threads`: Number of parallel downloads (default: 1)

## Output Structure

```
downloads/
├── reel_ID_1/
│   ├── video.mp4
│   └── metadata.json
└── reel_ID_2/
    ├── video.mp4
    └── metadata.json
```

## Metadata Example

```json
{
  "id": "ABC123DEF",
  "caption": "Amazing reel!",
  "likes": 1250,
  "comments": 45,
  "author": "username",
  "author_id": "12345",
  "created_at": "2024-01-15T10:30:00",
  "download_time": "2024-01-15T15:45:23"
}
```

## Requirements

- Python 3.8+
- Instagram account (optional, for private content)
- Internet connection

## Legal Disclaimer

This tool is for personal use only. Please respect Instagram's Terms of Service and copyright laws. Only download content you have permission to download.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please create an issue on GitHub.
