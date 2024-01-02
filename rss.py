import hashlib
import os
import re
import requests
from urllib.parse import urlparse, urlunparse
import uuid
import xml.etree.ElementTree as et
import mimetypes

MIMETYPE_REGEX = re.compile('(audio/.*)|(image/.*)')

# Returns the parsed URL if the input is a valid HTTP/S URI.
def parse_url(url):
  try:
    r = urlparse(url)
    return r if r.scheme == 'http' or r.scheme == 'https' else None
  except:
    return None

# Returns the extension of the resource pointed to by the URL.
def url_ext(url):
  rel_path = url.path.split('/')[-1]
  return rel_path.split('.')[-1] if '.' in rel_path else None

# Downloads the given URL to the given filename.
def download(url, f):
  try:
    response = requests.get(url)
    with open(f, 'wb') as file:
      file.write(response.content)
  except Exception as e:
    print(f'Error downloading {url}: {e}')

# Returns a (node, attrib, url) reference for each URL that appears
# in the node or its children. A 'None' attrib is used to signal
# that the URL is in the node's text instead of an attribute.
def find_urls(node):
  refs = []

  text_url = parse_url(node.text)
  if text_url:
    refs.append((node, None, text_url))  # None means URL in text.

  attr_urls = [(k, parse_url(v)) for k, v in node.attrib.items()]
  refs.extend([(node, k, v) for k, v in attr_urls if v])

  for child in node:
    refs.extend(find_urls(child))

  return refs


# TODO: rewrite node tree to reference new files uploaded on
# Google drive.
refs = find_urls(et.parse('../mini.rss').getroot())
file_refs = []

for node, attr, url in refs:
  ext = url_ext(url)
  mimetype, _ = mimetypes.guess_type(url.path)

  if not mimetype or not MIMETYPE_REGEX.match(mimetype):
    continue

  file_refs.append((node, attr, url, f'{hash_str(urlunparse(url))[-10:]}.{ext}', mimetype))

  # Skip already-downloaded files.
  if os.path.exists(file_refs[-1][-1]):
    continue

  print(f'Downloading {url} to {file_refs[-1][-1]}')
  download(urlunparse(url), file_refs[-1][-1])
  print('Done')

print([(attr, urlunparse(url), fn) for _, attr, url, fn, _ in file_refs])
