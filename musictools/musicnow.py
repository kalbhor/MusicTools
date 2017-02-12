#!/usr/bin/env python

import requests
import youtube_dl
from collections import OrderedDict
from bs4 import BeautifulSoup


class MusicNow(object):
    """
    Fetch list of videos from youtube,
    download audio from selected video
    """

    YOUTUBECLASS = 'spf-prefetch'

    def __init__(self):
        pass

    @staticmethod
    def get_url(song_input):
        """
        Gather all urls, titles for a search query
        from youtube
        """

        html = requests.get("https://www.youtube.com/results",
                            params={'search_query': song_input})
        soup = BeautifulSoup(html.text, 'html.parser')

        soup_section = soup.findAll('a', {'rel': MusicNow.YOUTUBECLASS})

        # Use generator over list, since storage isn't important
        song_urls = ('https://www.youtube.com' + i.get('href')
                     for i in soup_section)
        song_titles = (i.get('title') for i in soup_section)

        youtube_list = list(zip(song_urls, song_titles))

        return youtube_list

    @staticmethod
    def download_song(song_url, song_title, location):
        """
        Download a song using youtube url and song title
        """
        outtmpl = song_title + '.%(ext)s'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': location + outtmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
                {'key': 'FFmpegMetadata'},
            ],

        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(song_url, download=True)
