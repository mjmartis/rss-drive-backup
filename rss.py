import hashlib
import mimetypes
import os
import re
import requests
from urllib.parse import urlparse, urlunparse
import uuid
import xml.etree.ElementTree as et

MIMETYPE_REGEX = re.compile('(audio/.*)|(image/.*)')

# Returns the hash of the given string.
def hash_str(s):
  sha256_hash = hashlib.sha256()
  sha256_hash.update(s.encode('utf-8'))
  return sha256_hash.hexdigest()

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

# Returns a (node, attrib, url, ext, mimetype) tuple for each
# URL appearing in the tree that is considered a piece of media
# that should be backed up.
def find_media_urls(root):
  refs = find_urls(root)
  media_refs = []

  for node, attr, url in refs:
    ext = url_ext(url)
    mimetype, _ = mimetypes.guess_type(url.path)

    if not mimetype or not MIMETYPE_REGEX.match(mimetype):
      continue

    media_refs.append((node, attr, urlunparse(url), ext, mimetype))

  return media_refs
