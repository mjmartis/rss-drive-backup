import os

import gcreds
import gdrive

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
import requests
import hashlib
from urllib.parse import urlparse, urlunparse

NAME = 'Reupload test'
FILE_CHUNK_SIZE_BYTES = 5 * 1024 * 1024 # 5MB.

# Returns the hash of the given string.
def hash_str(s):
  sha256_hash = hashlib.sha256()
  sha256_hash.update(s.encode('utf-8'))
  return sha256_hash.hexdigest()

def reupload(in_url, mimetype, filename, gdrive_session, gdrive_permissions, folder_id):
  # Attempt download.
  resp = requests.get(in_url, stream=True)
  if resp.status_code != 200:
    return None

  # Stream file onto disk.
  with open(filename, 'ab+') as tmp_file:
    for chunk in resp.iter_content(chunk_size=FILE_CHUNK_SIZE_BYTES):
      tmp_file.write(chunk)
    tmp_file.seek(0)

    # Upload file to Google drive.
    metadata = {'name': filename, 'mimeType': mimetype, 'parents': [folder_id]}
    file_id = gdrive.upload_file(gdrive_session, metadata, tmp_file)
  os.remove(filename)

  # Share Google drive file.
  gdrive.enable_sharing_for_file(gdrive_permissions, file_id)

  return f'https://drive.google.com/uc?id={file_id}'

def main():
  creds = gcreds.get_gcreds()

  # Session is used to fallback to HTTP requests when we can't use
  # the client library.
  session = AuthorizedSession(creds)
  service = build('drive', 'v3', credentials=creds)

  # Create new folder to hold media.
  if gdrive.find_folder_id(service.files(), NAME):
    print(f'Folder "{NAME}" already exists; aborting.')
    exit(1)
  folder_id = gdrive.create_new_folder(service.files(), NAME)

  url = 'replace with test url'
  print(reupload(url, 'image/jpeg', f'{hash_str(url)[-10:]}.jpg', session, service.permissions(), folder_id))

if __name__ == '__main__':
  main()
