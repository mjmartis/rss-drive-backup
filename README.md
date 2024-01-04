# RSS Google Drive backup #

This script automatically uploads media from an RSS feed to Google Drive and
produces a copy of the RSS file that references these media. The new feed can
then be used even if you lose access to the original.

To set up permissions and dependencies, follow the
[Google Drive Python API quickstart guide](https://developers.google.com/drive/api/quickstart/python)
and install the `requests` library. You can then produce the backup feed by
running `python3 main.py <RSS file>`.

Streaming from Google Drive appears to be unreliable, so instruct your app of
choice to pre-download media if you have trouble.
