import sys
import spotipy
import spotipy.util as util
import os
from random import shuffle
from spotipy.oauth2 import SpotifyClientCredentials

os.environ['SPOTIPY_CLIENT_ID'] = "1a5bd897bf2b4e5fa1fc856baad745a8"
os.environ['SPOTIPY_REDIRECT_URI'] = "http://localhost:5000/"
scope = 'user-library-read playlist-modify-private user-read-private playlist-read-collaborative playlist-read-private'


class Song:
    name = ""
    duration = 0.0
    uri = ""

    def __init__(self, name, duration, uri):
        self.name = name
        self.duration = duration
        self.uri = uri


def make_song_list(new_songs, song_list=[]):  # makes or adds to the song list given a dict
    for song in new_songs:
        song_list.append(song)
    return song_list


def get_playlist_songs(username, sp, playlist_name):  # gets song name and duration of each song in a playlist
    playlists = get_playlists(username, sp)
    uri = ''
    songs_list = []
    for playlist in playlists:
        if playlists[playlist]['uri'] == playlist_name:
            uri = playlists[playlist]['uri']
    tracks = sp.user_playlist(username, uri)
    for song in tracks["tracks"]["items"]:
        song_uri = song['track']['uri']
        song_name = song['track']['name']
        song_duration = song['track']['duration_ms']
        songs_list.append(Song(song_name, song_duration, song_uri))
    return songs_list


def get_playlists(username, sp):  # gets all of user's playlists; returns playlist name and playlist uri dict
    list = {}
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        tracks = sp.user_playlist(username, playlist['uri'])
        length = 0
        for song in tracks['tracks']['items']:
            length += song['track']['duration_ms']
        list[playlist['name']] = {"uri": playlist['uri'],
                                  "tracks": playlist['tracks']['total'],
                                  "length": int(round(length / 60000)),
                                  "name": playlist['name']}
    return list




def get_playlist_length(username, sp, playlist_name):
    playlists = get_playlists(username, sp)
    length = 0
    if playlist_name in playlists.keys():
        uri = playlists[playlist_name]
    tracks = sp.user_playlist(username, uri)
    for song in tracks["tracks"]["items"]:
        length += song['track']['duration_ms']
    return length


def get_library_songs(sp):  # gets song name and duration of each song in the user's library
    list = sp.current_user_saved_tracks(50)
    songs = list['items']
    songs_list = []
    for song in songs:
        song_uri = song['track']['uri']
        song_name = song['track']['name']
        song_duration = song['track']['duration_ms']
        songs_list.append(Song(song_name, song_duration, song_uri))
    return songs_list


def make_playlist(username, name, length, long_songs, sp):  # creates the playlist that satisfies the time constraint,
    # returns duration
    shuffle(long_songs)
    new_songs = []
    current_length = 0
    description = 'A(n) ~' + str(length) + ' minute long playlist!'
    target = min_to_ms(int(length))  # 120000ms = 2 min
    for i in range(0, len(long_songs)):
        if current_length + long_songs[i].duration < target + 120000:
            new_songs.append(long_songs[i].uri)
            current_length += long_songs[i].duration
        if current_length < target - 120000:
            new_songs.append(long_songs[-1].uri)
            current_length += long_songs[-1].duration
    response = sp.user_playlist_create(username, name, False)  # create playlist
    link = response['external_urls']['spotify']
    uri = get_playlist_uri(name, sp, username)
    sp.user_playlist_add_tracks(username, uri, new_songs)  # add song to playlist
    return link

def get_playlist_uri(name, sp,username):
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['name'] == name:
            return playlist['uri']


def authenticate():
    token = util.prompt_for_user_token("user", scope)
    if token:
        return token
    else:
        return "FAILED"


def min_to_ms(minutes):
    return minutes * 60 * 1000


