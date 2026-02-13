# Automated Video Pipeline for YouTube Shorts
# This script automates the entire process: content generation, video production, and upload.

import os
import random
import datetime
import subprocess
from pathlib import Path

import openai
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# Configuration
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
DALL_E_API_URL = "https://api.openai.com/v1/images/generations"
YOUTUBE_UPLOAD_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]
VIDEO_OUTPUT_DIR = Path("output_videos")
LOG_FILE = Path("pipeline_log.txt")
VIDEO_FORMAT = "mp4"
BG_AUDIO_DIR = Path("bg_audio_tracks")
REQUEST_TIMEOUT_SECONDS = 30

# Logging Function
def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")
    print(message)


def get_openai_api_key():
    api_key = os.getenv(OPENAI_API_KEY_ENV)
    if not api_key:
        raise EnvironmentError(
            f"Missing {OPENAI_API_KEY_ENV}. Set it in your environment before running."
        )
    return api_key


def ensure_output_dir():
    if not VIDEO_OUTPUT_DIR.exists():
        VIDEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def escape_drawtext(text):
    # Escape characters that break ffmpeg drawtext parsing.
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
    )

# Generate Text Content
def generate_text():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant generating inspirational quotes."},
                {"role": "user", "content": "Generate a short inspirational quote in English."}
            ]
        )
        text = response['choices'][0]['message']['content'].strip()
        log_message(f"Generated text: {text}")
        return text
    except Exception as e:
        log_message(f"Error generating text: {e}")
        return "Keep pushing forward with positivity!"

# Generate Image with DALL-E
def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    response = requests.post(
        DALL_E_API_URL,
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS
    )
    response.raise_for_status()
    response_json = response.json()
    if 'data' not in response_json or len(response_json['data']) == 0:
        log_message("Failed to generate image from DALL-E API.")
        raise ValueError("Failed to generate image from DALL-E API.")
    image_url = response_json['data'][0]['url']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = VIDEO_OUTPUT_DIR / f"background_{timestamp}.png"
    image_response = requests.get(image_url, timeout=REQUEST_TIMEOUT_SECONDS)
    image_response.raise_for_status()
    image_path.write_bytes(image_response.content)
    log_message(f"Generated image saved to {image_path}")
    return str(image_path)

# Select Random Background Music
def select_random_audio():
    audio_files = [
        path for path in BG_AUDIO_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".mp3"
    ]
    if not audio_files:
        log_message("No audio tracks found in the directory.")
        raise FileNotFoundError("No audio tracks found in the directory.")
    audio_file = random.choice(audio_files)
    log_message(f"Selected audio file: {audio_file}")
    return str(audio_file)

# Create Video with FFmpeg
def create_video(text, image_path, audio_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = VIDEO_OUTPUT_DIR / f"output_video_{timestamp}.{VIDEO_FORMAT}"
    font_file = "./assets/roboto.ttf"  # Altere para o caminho correto da sua fonte

    escaped_text = escape_drawtext(text)
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-loop", "1",
                "-i", image_path,
                "-i", audio_path,
                "-vf",
                (
                    "drawtext="
                    f"fontfile={font_file}:"
                    f"text='{escaped_text}':"
                    "fontcolor=white:fontsize=48:"
                    "x=(w-text_w)/2:y=(h-text_h)/2"
                ),
                "-t", "00:00:30",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                str(output_file)
            ],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else "(no ffmpeg stderr)"
        log_message(f"FFmpeg failed: {stderr}")
        raise

    log_message(f"Created video: {output_file}")
    return str(output_file)

# Upload Video to YouTube
def upload_video(video_file, title, description, tags):
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    if not Path(client_secrets_file).is_file():
        log_message("Missing client_secret.json for YouTube upload.")
        raise FileNotFoundError("client_secret.json not found.")

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, YOUTUBE_UPLOAD_SCOPE
    )
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"  # People & Blogs
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    log_message(f"Upload completed: {response}")
    return response

# Main Workflow
def main():
    try:
        openai.api_key = get_openai_api_key()
    except EnvironmentError as exc:
        log_message(str(exc))
        return

    ensure_output_dir()

    text_content = generate_text()
    try:
        image_file = generate_image(text_content)
    except ValueError as e:
        log_message(str(e))
        return

    audio_file = select_random_audio()

    video_file = create_video(text_content, image_file, audio_file)

    try:
        upload_video(
            video_file,
            f"Inspirational Quote: {text_content[:30]}...",
            text_content,
            ["Motivation", "Inspirational", "Shorts"]
        )
    except Exception as exc:
        log_message(f"Upload failed: {exc}")
        return

if __name__ == "__main__":
    main()
