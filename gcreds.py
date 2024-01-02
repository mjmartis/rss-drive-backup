# Taken from:
#  https://developers.google.com/drive/api/quickstart/python

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

CREDS_JSON = 'credentials.json'
TOKEN_JSON = 'token.json'

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Loads credentials from either a cached token file or through a web flow.


def get_gcreds():
  creds = None

  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(TOKEN_JSON):
    creds = Credentials.from_authorized_user_file(TOKEN_JSON, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(CREDS_JSON, SCOPES)
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(TOKEN_JSON, 'w') as token:
      token.write(creds.to_json())

  return creds
