import os
import json
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pytube import YouTube

# Define your YouTube channel ID
channel_id = "your_channel_id"

# Define paths
download_path = "downloaded_video.mp4"
credentials_path = "path/to/your/credentials.json"

# YouTube Data API scopes
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_latest_video_id(channel_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)

    # Get the latest video uploaded to the channel
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        maxResults=1,
        type="video"
    )
    response = request.execute()

    # Extract the video ID
    latest_video_id = response["items"][0]["id"]["videoId"]
    return latest_video_id

def download_video(video_url, output_path):
    try:
        yt = YouTube(video_url)
        # Select the highest resolution stream
        stream = yt.streams.get_highest_resolution()
        # Download the video
        stream.download(output_path)
        print("Video downloaded successfully.")
        return True
    except Exception as e:
        print("Error downloading video:", str(e))
        return False

def upload_video(credentials_path, video_path):
    # Authorize access to the YouTube Data API
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
    credentials = flow.run_console()
    youtube = build("youtube", "v3", credentials=credentials)

    # Upload video to YouTube
    request_body = {
        "snippet": {
            "title": "Uploaded video title",
            "description": "Uploaded video description",
            "tags": ["tag1", "tag2"]
        },
        "status": {
            "privacyStatus": "private"  # Change to "public" if desired
        }
    }

    media_file = MediaFileUpload(video_path)
    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    ).execute()

    print("Video uploaded successfully.")
    print("Video ID:", response["id"])

if __name__ == "__main__":
    # Get the latest video ID from your channel
    #api_key = "your_api_key"
    #latest_video_id = get_latest_video_id(channel_id, api_key)
    latest_video_id = 'mK2FOUoBBYc'

    # Construct the URL of the latest video
    video_url = f"https://www.youtube.com/watch?v={latest_video_id}"

    # Download the latest video
    download_video(video_url, download_path)

    # Upload the downloaded video
    #upload_video(credentials_path, download_path)
