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

from mutagen.id3 import ID3, APIC, _util
from mutagen.mp3 import EasyMP3
import spotipy
from urllib.request import urlopen

from .improve import improve_name, img_search_google


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
    def download_song(song_url, song_title):
	    outtmpl = song_title + '.%(ext)s'
	    ydl_opts = {
	        'format': 'bestaudio/best',
	        'outtmpl': outtmpl,
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


class MusicRepair(object):

    def __init__(self):
        pass


    @staticmethod
    def get_details_spotify(file_name):
        '''
        Tries finding metadata through Spotify
        '''

        song_name = improve_name(file_name)

        spotify = spotipy.Spotify()
        results = spotify.search(song_name, limit=1)  # Find top result
        try:
            album = (results['tracks']['items'][0]['album']
                     ['name'])  # Parse json dictionary
            artist = (results['tracks']['items'][0]['album']['artists'][0]['name'])
            song_title = (results['tracks']['items'][0]['name'])

            return artist, album, song_title, ''


        except Exception as error:
            return ' ',' ', song_name, error

    @staticmethod
    def add_albumart(file_name, song_title):

        albumart = img_search_google(song_title)
        try:
            img = urlopen(albumart)  # Gets album art from url

        except Exception:
            return None

        audio = EasyMP3(file_name, ID3=ID3)
        try:
            audio.add_tags()
        except _util.error:
            pass

        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/png',
                type=3,  # 3 is for album art
                desc='Cover',
                data=img.read()  # Reads and adds album art
            )
        )
        audio.save()

        return albumart


    @staticmethod
    def add_details(file_name, title, artist, album):
        tags = EasyMP3(file_name)
        tags["title"] = title
        tags["artist"] = artist
        tags["album"] = album
        tags.save()

