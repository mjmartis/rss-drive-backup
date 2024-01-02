from datetime import datetime
import hashlib
import io
import os
import sys
import xml.etree.ElementTree as et

import gcreds
import gdrive
import rss

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
import requests

FILE_CHUNK_SIZE_BYTES = 5 * 1024 * 1024  # 5MB.
SHARE_URL = 'https://drive.google.com/uc?id={}'

# Returns the hash of the given string.
def hash_str(s):
  sha256_hash = hashlib.sha256()
  sha256_hash.update(s.encode('utf-8'))
  return sha256_hash.hexdigest()


def reupload(info_str, in_url, filename, mimetype, gdrive_session, gdrive_permissions, folder_id):
  # Attempt download.
  print(f'Downloading {info_str}...', end='', flush=True)
  resp = requests.get(in_url, stream=True)
  if resp.status_code != 200:
    return None

  # Stream file onto disk.
  with open(filename, 'ab+') as tmp_file:
    for chunk in resp.iter_content(chunk_size=FILE_CHUNK_SIZE_BYTES):
      tmp_file.write(chunk)
    tmp_file.seek(0)
    print('done', flush=True)

    # Upload file to Google drive.
    metadata = {'name': filename, 'mimeType': mimetype, 'parents': [folder_id]}
    print(f'Reuploading {info_str}...', end='', flush=True)
    file_id = gdrive.upload_file(gdrive_session, metadata, tmp_file)
    print('done', flush=True)
  os.remove(filename)

  # Share Google drive file.
  gdrive.enable_sharing_for_file(gdrive_permissions, file_id)

  return SHARE_URL.format(file_id)


def main():
  if len(sys.argv) != 2:
    print(f'Usage: python3 {sys.argv[0]} <rss feed file>')
    exit(1)

  creds = gcreds.get_gcreds()

  # Session is used to fallback to HTTP requests when we can't use
  # the client library.
  session = AuthorizedSession(creds)
  service = build('drive', 'v3', credentials=creds)

  # Load RSS feed.
  feed = et.parse(sys.argv[1]).getroot()

  # Compose the name of the new Google drive folder for our media.
  folder_name = f'[RSS Backup {datetime.now().strftime("%d %b %Y")}]'
  title = feed.find('./channel/title')
  if title is not None:
    folder_name += f' {title.text}'

  # Create the new Google drive folder.
  if gdrive.find_folder_id(service.files(), folder_name):
    print(f'Folder "{folder_name}" already exists; aborting.')
    exit(1)
  folder_id = gdrive.create_new_folder(service.files(), folder_name)

  # Reupload each unique piece of media.
  url_refs = rss.find_media_urls(feed)
  seen = {}
  gdrive_urls = []
  for i, (_, _, url, ext, mimetype) in enumerate(url_refs):
    if url in seen:
      gdrive_urls.append(seen[url])
      continue

    filename = f'{hash_str(url)[-10:]}.{ext}'
    gdrive_url = reupload(f'{i+1}/{len(url_refs)}', url, filename, mimetype, session,
                          service.permissions(), folder_id)

    if not gdrive_url:
      print(f'Error reuploading "{url}"; aborting.')
      exit(1)

    seen[url] = gdrive_url
    gdrive_urls.append(gdrive_url)

  # Update URLs in the feed.
  for (node, attrib, _, _, _), url in zip(url_refs, gdrive_urls):
    if not attrib:
      node.text = url
    else:
      node.attrib[attrib] = url

  # Upload the new feed.
  feed_str = et.tostring(feed, encoding='utf8')
  metadata = {'name': 'feed.rss',
              'mimeType': 'application/rss+xml', 'parents': [folder_id]}
  feed_id = gdrive.upload_file(session, metadata, io.BytesIO(feed_str))
  gdrive.enable_sharing_for_file(service.permissions(), feed_id)
  print(SHARE_URL.format(feed_id))


if __name__ == '__main__':
  main()
