from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
app.secret_key = 'moms-and-pops'  # CHANGE THIS VALUE

PASSWORD = '2girlsand2boys'  # <-- Set your desired password here

def extract_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ['www.youtube.com', 'youtube.com']:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith('/embed/'):
            return query.path.split('/')[2]
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('authenticated'):
        return render_template('login.html')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    pw = request.form.get('password')
    if pw == PASSWORD:
        session['authenticated'] = True
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error='Incorrect password.')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('index'))

@app.route('/transcript', methods=['POST'])
def get_transcript():
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json()
    video_url = data.get('url')
    video_id = extract_video_id(video_url)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = "\n".join([entry["text"] for entry in transcript])
        return jsonify({"transcript": text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
