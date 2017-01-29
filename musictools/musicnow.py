#!/usr/bin/env python

"""
  __  __           _      _   _
 |  \/  |_   _ ___(_) ___| \ | | _____      __
 | |\/| | | | / __| |/ __|  \| |/ _ \ \ /\ / /
 | |  | | |_| \__ \ | (__| |\  | (_) \ V  V /
 |_|  |_|\__,_|___/_|\___|_| \_|\___/ \_/\_/

"""

from bs4 import BeautifulSoup
import requests
import youtube_dl

from collections import OrderedDict

class MusicNow(object):

    YOUTUBECLASS = 'spf-prefetch'

    def __init__(self):
        pass

    @staticmethod
    def get_url(song_input):

        youtube_urls = []
        youtube_titles = []
        num = 0  # List of songs index

        html = requests.get("https://www.youtube.com/results",
		                    params={'search_query': song_input})
        soup = BeautifulSoup(html.text, 'html.parser')

        youtube_list = OrderedDict()

		# In all Youtube Search Results

        for i in soup.findAll('a', {'rel': MusicNow.YOUTUBECLASS}):
            song_url = 'https://www.youtube.com' + (i.get('href'))
            song_title = (i.get('title'))
            youtube_list.update({song_title: song_url})

        return youtube_list

    @staticmethod
    def download_song(song_url, song_title, location):
	    outtmpl = song_title + '.%(ext)s'
	    ydl_opts = {
	        'format': 'bestaudio/best',
	        'outtmpl': location+outtmpl,
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
