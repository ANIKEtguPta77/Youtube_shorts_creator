import os
import numpy as np

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YoutubeClientUpload:
    def __init__(self) -> None:
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        self.CLIENT_SECRETS_FILE = "client_secret_cutevibes.json" # your client secret json from youtube v3 api
        self.youtube = self.authenticate_youtube_api()

    def authenticate_youtube_api(self):
        creds = None
        
        # Check if the token.json file already exists to use existing credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # If no valid credentials, allow user to login and get a new one
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRETS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return build('youtube', 'v3', credentials=creds)

    def upload_video(self, video_file, title, description, tags, category):
        # Youtube video category
        # https://gist.github.com/dgp/1b24bf2961521bd75d6c
        if category == "human":
            category_id = 22 
        elif category == "animal":
            category_id = 15
        else:
            category_id = 31
        
        privacy_status="public"

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        # The video file should be less than 60 seconds to qualify as a YouTube Short
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/mp4")

        # Call the API to upload the video
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = request.execute()

        print(f"Video uploaded. Video ID: {response['id']}")
