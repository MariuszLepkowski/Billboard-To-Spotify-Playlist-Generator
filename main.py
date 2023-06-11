import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-modify-private",
    show_dialog=True,
    cache_path="token.txt"
)

sp = spotipy.Spotify(auth_manager=auth_manager)
user_id = sp.current_user()["id"]

user_date_of_choice = input(
    "Which year do you want to travel to?\n"
    "Type the date in this format YYYY-MM-DD: "
)

chart_url = f"https://www.billboard.com/charts/hot-100/{user_date_of_choice}"

response = requests.get(url=chart_url)
chart_html = response.text

soup = BeautifulSoup(chart_html, "html.parser")
song_names_spans = soup.select("li ul li h3")
artists_spans = soup.select("li ul li span")

song_names = [song.getText().strip() for song in song_names_spans]
artist_names = [artist.getText().strip() for artist in artists_spans[0::7]]

songs = list(zip(artist_names, song_names))

song_uris = []
for song in songs:
    try:
        results = sp.search(q=song, type="track", market="US")
        song_uri = results["tracks"]["items"][0]["uri"]
        print(song_uri)
        song_uris.append(song_uri)
    except spotipy.exceptions.SpotifyException:
        continue


new_playlist = sp.user_playlist_create(user=user_id, name=f"{user_date_of_choice} Billboard 100", public=False)
new_playlist_id = new_playlist["id"]

my_playlist = sp.playlist_add_items(playlist_id=new_playlist_id, items=song_uris)

