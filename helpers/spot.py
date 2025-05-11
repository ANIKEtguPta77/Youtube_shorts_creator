import os
import requests

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import warnings


class SpotifyClient:
    def __init__(self):
        CLIENT_ID = '2bec4819b43c49148589b1b01c25a01d'
        CLIENT_SECRET = '8880dfbc3efd4acfa95ae6ef7dce9cc7'
        client_credentials = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials)
        warnings.filterwarnings("ignore", category=ResourceWarning)
        self.max_results = 10

    def _search_music(self, query):
        results = self.sp.search(q=query, type='track', limit=self.max_results)
        tracks = results['tracks']['items']
        
        music_list = []
        for track in tracks:
            music_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'url': track['external_urls']['spotify'],
            'preview_url': track['preview_url'] # This URL is a short preview of the track
            }
            music_list.append(music_info)

        return music_list

    def _download_audio_file(self, preview_url, file_name, folder_name): 
        response = requests.get(preview_url)
        
        if response.status_code == 200: 
            file_path = os.path.join(folder_name, file_name)
            with open(file_path, 'wb') as audio_file:
                audio_file.write(response.content)
            
            print(f"Downloaded: {file_name}")
        else:
            print(f"Failed to download audio: {response.status_code}")
        
    def download_audio(self, query = "background music for cute baby clips", folder_name = "."):
        music_results = self._search_music(query)
        music_results = music_results

        for i, music in enumerate(music_results, start=1):
            print(f"{i}. {music['name']} by {music['artist']}")
            print(f" Listen here: {music['url']}")
            if music['preview_url']:
                print(f" Preview: {music['preview_url']}")
                # Download the audio preview
                file_name = f"{music['name'].replace(' ', '_')}.mp3" # Generate file name 
                self._download_audio_file(music['preview_url'], file_name, folder_name)
                return f"Listen to '{music['name']}' by {music['artist']} at: {music['url']}" 
            else:
                print(f" No preview available")
        
        return None
