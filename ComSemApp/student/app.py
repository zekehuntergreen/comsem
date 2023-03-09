from flask import Flask, request, jsonify
import requests

#Currently setup with flask
#use flask run and go to http://localhost:5000/search_videos?query=replace_with_search

app = Flask(__name__)

API_KEY = "1330c216-9f26-4c1f-813c-4665a8918c30"

@app.route('/search_videos')
def search_videos():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Please provide a query parameter'}), 400
    
    headers = {'Authorization': 'Bearer ' + API_KEY}
    url = f"https://youglish.com/api/v1/videos/search?key={API_KEY}&query={query}&lg=english"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to search videos'}), response.status_code
    
    videos = response.json()
    return jsonify(videos)

@app.route('/get_video')
def get_video():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({'error': 'Please provide a video_id parameter'}), 400
    
    headers = {'Authorization': 'Bearer ' + API_KEY}
    url = f"https://youglish.com/api/v1/videos/{video_id}"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to get video'}), response.status_code
    
    video = response.json()
    return jsonify(video)

if __name__ == '__main__':
    app.run(debug=True)
