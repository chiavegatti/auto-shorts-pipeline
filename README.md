# Auto Shorts

Automates a simple pipeline to generate a quote, create a background image, render a short video with FFmpeg, and upload to YouTube.

## Requirements

- Python 3.10+
- FFmpeg installed and available in PATH
- A Google OAuth client file named `client_secret.json`
- An OpenAI API key set in the environment

## Setup

1) Create and activate a virtual environment.
2) Install dependencies:

```
pip install -r requirements.txt
```

3) Set environment variables:

```
# PowerShell
$env:OPENAI_API_KEY = "your_api_key"
```

4) Add at least one MP3 file to `bg_audio_tracks/`.

## Run

```
python auto_shorts.py
```

## Notes

- Outputs are written to `output_videos/`.
- Logs are written to `pipeline_log.txt`.
- The YouTube upload step uses OAuth and will prompt in the console.
