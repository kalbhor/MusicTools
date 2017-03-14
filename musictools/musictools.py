#!/usr/bin/env python

import requests
import youtube_dl
import spotipy
import os
from mutagen.id3 import ID3, APIC, _util
from mutagen.mp3 import EasyMP3
from bs4 import BeautifulSoup
from urllib.request import urlopen
from .improve import improve_name, img_search_google


def get_song_urls(song_input):
    """
    Gather all urls, titles for a search query
    from youtube
    """
    YOUTUBECLASS = 'spf-prefetch'

    html = requests.get("https://www.youtube.com/results",
                        params={'search_query': song_input})
    soup = BeautifulSoup(html.text, 'html.parser')

    soup_section = soup.findAll('a', {'rel': YOUTUBECLASS})

    # Use generator over list, since storage isn't important
    song_urls = ('https://www.youtube.com' + i.get('href')
                 for i in soup_section)
    song_titles = (i.get('title') for i in soup_section)

    youtube_list = list(zip(song_urls, song_titles))

    del song_urls
    del song_titles

    return youtube_list


def download_song(song_url, song_title, dl_directory='./'):
    """
    Download a song using youtube url and song title
    """
    global location

    dl_directory = os.path.abspath(os.path.expanduser(dl_directory))

    location = dl_directory
    outtmpl = song_title + '.%(ext)s'
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(location, outtmpl),
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


def get_metadata(file_name):
    """
    Tries finding metadata through Spotify
    """

    song_name = improve_name(file_name)  # Remove useless words from title

    spotify = spotipy.Spotify()
    results = spotify.search(song_name, limit=1)
    try:
        results = results['tracks']['items'][0]  # Find top result
        album = (results['album']
                 ['name'])  # Parse json dictionary
        artist = (results['album']['artists'][0]['name'])
        song_title = (results['name'])
        albumart = (results['album']['images'][0]['url'])

        return artist, album, song_title, albumart

    except Exception as error:
        print(error)
        return 'Unknown', 'Unknown', song_name, None


def add_albumart(file_name, albumart=None):
    """
    Add albumart in .mp3's tags
    """
    file_name = os.path.abspath(os.path.join(location, file_name + '.mp3'))

    if albumart is None:
        albumart = img_search_google(file_name)

    img = urlopen(albumart)  # Gets album art from url
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


def add_metadata(file_name, title, artist, album):
    """
    As the method name suggests
    """
    file_name = os.path.abspath(os.path.join(location, file_name + '.mp3'))
    
    tags = EasyMP3(file_name)
    tags["title"] = title
    tags["artist"] = artist
    tags["album"] = album
    tags.save()

    return file_name
