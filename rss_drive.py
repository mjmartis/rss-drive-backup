import requests
from urllib.parse import urlparse, urlunparse
import uuid
import xml.etree.ElementTree as et

BACKUP_EXTS = ['mp3']

# Returns the parsed URL if the input is a valid HTTP/S URI.
def parse_url(url):
  try:
    r = urlparse(url)
    return r if r.scheme == 'http' or r.scheme == 'https' else None
  except:
    return None

# Returns the extension of the resource pointed to by the URL.
def url_ext(url):
  rel_path = urlparse(url).path.split('/')[-1]
  return rel_path.split('.')[-1] if '.' in rel_path else None

# Downloads the given URL to the given filename.
def download(url, f):
  try:
    response = requests.get(url)
    with open(f, 'wb') as file:
      file.write(response.content)
  except Exception as e:
    print(f'Error downloading {url}: {e}')

# Returns a (node, attrib) reference for each URL that appears
# in the node or its children. A 'None' attrib is used to signal
# that the URL is in the node's text instead of an attribute.
def find_urls(node):
  refs = []
  
  text_url = parse_url(node.text)
  if text_url:
    refs += [(node, None)]  # None means URL in text.

  attr_urls = [(k, parse_url(v)) for k, v in node.attrib.items()]
  refs += [(node, k) for k, v in attr_urls if v]

  for child in node:
    refs += find_urls(child)

  return refs

# TODO: rewrite node tree to reference new files uploaded on
# Google drive.
refs = find_urls(et.parse('glasscannon.rss').getroot())
file_refs = []

for node, attr in refs:
  url = node.attrib[attr] if attr else node.text
  ext = url_ext(url)

  if ext not in BACKUP_EXTS:
    file_refs.append(None)
    continue

  file_refs.append(f'{str(uuid.uuid4().hex)[:10]}.{ext}')
  print(f'Downloading {url} to {file_refs[-1]}')
  download(url, file_refs[-1])
  print('Done')
