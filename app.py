import os
import yt_dlp as ytdl
from flask import Flask, jsonify, request
from googleapiclient.discovery import build
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins (adjust if needed)

# Load API key from environment variable
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    raise EnvironmentError("YOUTUBE_API_KEY is not set. Please add it in Render's environment variables.")

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200


@app.route('/search', methods=['GET'])
def search_music():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        search_response = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            maxResults=10
        ).execute()

        results = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'

            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'skip_download': True,
                    'noplaylist': True,
                    'socket_timeout': 10,
                }
                with ytdl.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(video_url, download=False)

                # Include only if yt-dlp succeeded
                results.append({
                    'id': item['id'],
                    'snippet': item['snippet']
                })

                if len(results) == 5:
                    break

            except Exception as e:
                print(f"Skipping {video_id} due to extract error: {e}")
                continue

        if not results:
            return jsonify({"error": "No playable videos found."}), 404

        return jsonify(results)

    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": "Failed to search or filter YouTube results."}), 500


@app.route('/play', methods=['GET'])
def play_music():
    video_id = request.args.get('videoId')
    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400

    try:
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'skip_download': True,
            'noplaylist': True,
            'socket_timeout': 10,
        }

        with ytdl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get("formats", [])
            audio_url = next(
                (f.get('url') for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none'),
                None
            )

            if not audio_url:
                return jsonify({"error": "No audio stream found."}), 404

        return jsonify({'url': audio_url})

    except ytdl.utils.DownloadError as e:
        print(f"DownloadError: {e}")
        return jsonify({"error": "YouTube video is unavailable or restricted."}), 403

    except Exception as e:
        print(f"Playback error: {e}")
        return jsonify({"error": "Failed to extract audio from YouTube video."}), 500


if __name__ == '__main__':
    app.run(debug=True)
