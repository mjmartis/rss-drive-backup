import gcreds
import gdrive

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import google.auth.transport.requests

NAME = 'Test Folder'


def main():
  creds = gcreds.get_gcreds()

  # Session is used to fallback to HTTP requests when we can't use
  # the client library.
  session = google.auth.transport.requests.AuthorizedSession(creds)
  service = build('drive', 'v3', credentials=creds)

  # Create new folder to hold media.
  if gdrive.find_folder_id(service.files(), NAME):
    print(f'Folder "{NAME}" already exists; aborting.')
    exit(1)
  folder_id = gdrive.create_new_folder(service.files(), NAME)

  # Upload file.
  metadata = {'name': 'b41fb358d1.mp3',
              'mimeType': 'audio/mpeg', 'parents': [folder_id]}
  file_id = gdrive.upload_file(
      session, metadata, open('b41fb358d1.mp3', 'rb').read())
  gdrive.share_file_by_id(service.permissions(), file_id)

  print(f'https://drive.google.com/uc?id={file_id}')


if __name__ == '__main__':
  main()
