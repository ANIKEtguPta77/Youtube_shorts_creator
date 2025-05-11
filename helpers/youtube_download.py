import requests
import time, os
# import yt_dlp
from pytubefix import YouTube
from pytubefix.cli import on_progress
from googleapiclient.discovery import build
import moviepy.editor as mp


class YoutubeClientDownload:
    def __init__(self):
        youtube_api_key = "AIzaSyC-xe2hd3AHlraKuvJCkhG9b2by5UF8J1k"
        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
     
        self.max_search_results = 5

    def _is_short(self, video_id):
        try:
            url = f"https://www.youtube.com/shorts/{video_id}"
            response = requests.head(url, allow_redirects=False)

            if 300 <= response.status_code < 400:
                return False
            else:
                return True
            
        except requests.exceptions.RequestException as e:
            return False
        
    def _get_videos(self, query): 
        if "shorts" not in query:
            query += " shorts" 
        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            videoDuration="short", # Ensures we are searching for shorts (less than 60 seconds)
            maxResults=self.max_search_results
        )
        response = request.execute()
        return response.get('items', [])
        
    def _get_short_videos(self, query):
        items = self._get_videos(query)
        shorts_list = []
        for video in items:
            time.sleep(1)
            title = video['snippet']['title']
            video_id = video['id']['videoId']
            if not self._is_short(video_id): 
                continue 
            video_url = f"https://www.youtube.com/shorts/{video_id}" 
            # print(f"Title: {title}")
            # print(f"Video URL: {video_url}")
            # print()
            shorts_list.append((title, video_url)) 
        return shorts_list

    def _download_audio_from_shorts(self, video_id, output_path="downloads"):
        try:
            url = f"https://www.youtube.com/shorts/{video_id}"
            
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            
            # ydl_opts = {
            # 'format': 'bestaudio/best',
            # 'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            # 'postprocessors': [{
            # 'key': 'FFmpegExtractAudio',
            # 'preferredcodec': 'mp3',
            # 'preferredquality': '192',
            # }],
            # }
            
            # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # print(f"Downloading audio from: {url}")
            # ydl.download([url])
            yt = YouTube(url, on_progress_callback = on_progress,use_po_token=True)
            print(f"trying to download {yt.title}") 
            ys = yt.streams.get_audio_only()

            # Download the audio in webm format (default for audio-only streams)
            audio_file_path = os.path.join(output_path, yt.title + ".webm")
            ys.download(output_path=output_path, filename=yt.title + ".webm")

            # Convert to MP3 using moviepy
            mp3_file_path = os.path.join(output_path, yt.title + ".mp3")
            audio_clip = mp.AudioFileClip(audio_file_path)
            audio_clip.write_audiofile(mp3_file_path)

            # Clean up the original webm file
            os.remove(audio_file_path)

            print("Audio downloaded successfully.")
            return True 
        except Exception as e:
            print(f"An error occurred: {e}") 
            return False 
        
    def download_audio(self, query, output_path="downloads"):
        shorts_list = self._get_short_videos(query)
        for title, video_url in shorts_list:
            video_id = video_url.split('/')[-1]
            if self._download_audio_from_shorts(video_id, output_path): 
                return f"Listen to music '{title}' at: {video_url}"
        
        return None 