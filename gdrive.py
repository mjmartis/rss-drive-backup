# Based on
#  https://gist.githubusercontent.com/tanaikech/f709a952ff6e286027950d0484f6c03e/raw/b45787e303d5afc949c7ba41a5ecc79763a76eed/submit.md
import json
import os
import requests


ENDPOINT_URL = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable'
FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'
CHUNK_SIZE_BYTES = 5 * 1024 * 1024  # 5MB.
RETRIES = 3


def upload_file(session, metadata, data):
  # 1. Retrieve session for resumable upload.
  sess_resp = session.post(ENDPOINT_URL, json=metadata)
  location = sess_resp.headers['Location']

  # 2. Upload the file in chunks.
  dl = len(data)
  for start in range(0, dl, CHUNK_SIZE_BYTES):
    for attempt in range(RETRIES):
      end = min(start + CHUNK_SIZE_BYTES, dl)
      content_headers = {'Content-Range': f'bytes {start}-{end-1}/{dl}'}

      try:
        content_resp = session.put(
            location,
            headers=content_headers,
            data=data[start:end]
        )

        if content_resp.status != 200 and content_resp.status != 201 and \
           content_resp.status != 308:
          continue
      except:
        continue

      break

  return json.loads(content_resp.content)['id']


def find_folder_id(files, name):
  response = (
      files
      .list(
          q=f'mimeType="{FOLDER_MIMETYPE}" and name="{name}" and trashed=false',
          spaces='drive',
          fields='nextPageToken, files(id, name)',
      )
      .execute()
  )

  # Because we only see folders uploaded by this app, and this app only
  # uploads top-level folders, there should be exactly 0 or 1 results.
  items = response.get('files', [])
  return None if len(items) != 1 else items[0].get('id', None)


def create_new_folder(files, name):
  metadata = {'name': name, 'mimeType': FOLDER_MIMETYPE}
  return files.create(body=metadata, fields='id').execute()['id']


def share_file_by_id(permissions, id):
  permissions.create(
      body={'role': 'reader', 'type': 'anyone'}, fileId=id).execute()
