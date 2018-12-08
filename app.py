from flask import Flask,render_template,jsonify,request
from timefy import *
import spotipy
import sys
app = Flask(__name__)

SPOTIFY_CLIENT_ID = "1a5bd897bf2b4e5fa1fc856baad745a8"
SPOTIPY_CLIENT_SECRET = "640bcb54b8f745b1aa297b95f8075829"
SPOTIPY_REDIRECT_URI = "http://localhost:5000/login/"
scope = 'user-library-read playlist-modify-private user-read-private playlist-read-collaborative playlist-read-private'
token = None
username = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/playlists', methods=['GET','POST'])
def playlists():
    token = request.form['token']
    username = request.form['username']
    sp = spotipy.Spotify(auth=token)
    playlists = get_playlists(username,sp)
    data = {"playlists":playlists}
    print(playlists)
    return jsonify(data)

@app.route('/save', methods=['GET','POST'])
def save():
    token = request.form['token']
    username = request.form['username']
    playlisturi = request.form['playlist']
    length = request.form['length']
    playlistname = request.form['name']
    sp = spotipy.Spotify(auth=token)
    songs = get_playlist_songs(username, sp, playlisturi)
    link = make_playlist(username,playlistname,length,songs,sp)
    return jsonify(link)





