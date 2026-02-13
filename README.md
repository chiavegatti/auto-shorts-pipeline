# Auto Shorts

[![Repository](https://img.shields.io/badge/repo-auto--shorts--pipeline-2ea44f?logo=github)](https://github.com/chiavegatti/auto-shorts-pipeline)

Automates a simple pipeline to generate a quote, create a background image, render a short video with FFmpeg, and upload to YouTube.

## Purpose

Automatically generates a short video in the YouTube Shorts style: creates the quote, builds a background image, mixes audio, renders the video, and can upload to YouTube via OAuth. It is meant for fast production of motivational content with minimal manual work.

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

3) Create your environment file from the example and set variables:

```
copy .env-example .env
```

4) Set environment variables:

```
# PowerShell
$env:OPENAI_API_KEY = "your_api_key"
```

5) Replace the mock `client_secret.json` with your real Google OAuth client file.

6) Add at least one MP3 file to `bg_audio_tracks/`.

## Run

```
python auto_shorts.py
```

## Notes

- Outputs are written to `output_videos/`.
- Logs are written to `pipeline_log.txt`.
- The YouTube upload step uses OAuth and will prompt in the console.
- `client_secret.json` and `.env` are ignored by git for security.
