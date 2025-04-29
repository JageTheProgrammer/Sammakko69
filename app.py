import os
import yt_dlp as ytdl
from flask import Flask, jsonify, request
from googleapiclient.discovery import build
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Your YouTube API key (replace with your actual key)
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')


# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

@app.route('/search', methods=['GET'])
def search_music():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        # Call the YouTube API to search for the query
        search_response = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            maxResults=5
        ).execute()

        results = []
        for item in search_response.get('items', []):
            results.append({
                'id': item['id'],
                'snippet': item['snippet']
            })

        return jsonify(results)

    except Exception as e:
        print(f"Error during search: {e}")
        return jsonify({"error": "Failed to fetch data from YouTube"}), 500


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
        }

        with ytdl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)

            # Find audio-only format
            formats = info_dict.get("formats", [])
            audio_url = None
            for fmt in formats:
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    audio_url = fmt.get('url')
                    break

            if not audio_url:
                return jsonify({"error": "No audio stream found"}), 404

        return jsonify({'url': audio_url})

    except ytdl.utils.DownloadError as e:
        print(f"DownloadError during play: {e}")
        return jsonify({"error": "YouTube video is unavailable or restricted."}), 403
    except Exception as e:
        print(f"General error during play: {e}")
        return jsonify({"error": "Failed to extract audio from YouTube video"}), 500



if __name__ == '__main__':
    app.run(debug=True)
