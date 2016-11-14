#!/usr/bin/python

import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
CLIENT_SECRETS_FILE = "client_secrets.json"
CLIENT_SECRETS_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))
THIS_DIR = os.path.dirname(__file__)
# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class Youtube_API():
    def __init__(self, client_secrets_dir):
        self.client_secrets_dir = client_secrets_dir

    def get_playlist(self, playlistId):
        flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE_PATH,
                                       message=MISSING_CLIENT_SECRETS_MESSAGE,
                                       scope=YOUTUBE_READONLY_SCOPE)

        storage = Storage(os.path.abspath(os.path.join(THIS_DIR, "oauth2.json")))
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flags = argparser.parse_args()
            credentials = run_flow(flow, storage, flags)

        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        http=credentials.authorize(httplib2.Http()))

        # Retrieve the contentDetails part of the channel resource for the
        # authenticated user's channel.
        channels_response = youtube.channels().list(
            mine=True,
            part="contentDetails"
        ).execute()

        playlistitems_list_request = youtube.playlistItems().list(
            playlistId=playlistId,
            part="snippet",
            maxResults=50
        )

        output_data = []
        while playlistitems_list_request:
            playlistitems_list_response = playlistitems_list_request.execute()

            # Print information about each video.
            for playlist_item in playlistitems_list_response["items"]:
                title = playlist_item["snippet"]["title"]
                video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                output_data.append((title, video_id))

            playlistitems_list_request = youtube.playlistItems().list_next(
                playlistitems_list_request, playlistitems_list_response)
        return output_data

if __name__ == "__main__":
    playlistId = sys.argv[1] if len(sys.argv) > 1 else "PLgzTt0k8mXzEk586ze4BjvDXR7c-TUSnx"
    ya = Youtube_API("/home/luks/Documents/terceros/edu/synclist")
    for e in ya.get_playlist(playlistId):
        print(e)