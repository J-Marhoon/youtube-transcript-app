from flask import Flask, request, render_template, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

def extract_video_id(url):
    # Handle different YouTube URL formats
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ['www.youtube.com', 'youtube.com']:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith('/embed/'):
            return query.path.split('/')[2]
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    video_url = data.get('url')
    video_id = extract_video_id(video_url)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Format as plain text for demo
        text = "\n".join([entry["text"] for entry in transcript])
        return jsonify({"transcript": text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
