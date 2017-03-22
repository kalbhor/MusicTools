#!/usr/bin/env python

import requests
import youtube_dl
import spotipy
import os
import re
from mutagen.id3 import ID3, APIC, _util
from mutagen.mp3 import EasyMP3
from bs4 import BeautifulSoup
from urllib.request import urlopen

def improve_name(song_name):
    """
    Improves file name by removing words such as HD, Official,etc
    eg : Hey Jude (Official HD) lyrics -> Hey Jude
    This helps in better searching of metadata since a spotify search of
    'Hey Jude (Official HD) lyrics' fetches 0 results
    """

    try:
        song_name = os.path.splitext(song_name)[0]
    except IndexError:
        pass

    song_name = song_name.partition('ft')[0]

    # Words to omit from song title for better results through spotify's API
    chars_filter = "()[]{}-:_/=+\"\'"
    words_filter = ('official', 'lyrics', 'audio', 'remixed', 'remix', 'video',
                    'full', 'version', 'music', 'mp3', 'hd', 'hq', 'uploaded', 'explicit')

    # Replace characters to filter with spaces
    song_name = ''.join(
        map(lambda c: " " if c in chars_filter else c, song_name))

    # Remove crap words
    song_name = re.sub('|'.join(re.escape(key) for key in words_filter),
                       "", song_name, flags=re.IGNORECASE)

    # Remove duplicate spaces
    song_name = re.sub(' +', ' ', song_name)

    return song_name.strip()

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


def download_song(song_url, song_title):
    """
    Download a song using youtube url and song title
    """

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


def add_albumart(file_name, albumart):
    """
    Add albumart in .mp3's tags
    """

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
    
    tags = EasyMP3(file_name)
    tags["title"] = title
    tags["artist"] = artist
    tags["album"] = album
    tags.save()

    return file_name


def revert_music(files):
    """
    Removes all tags from a mp3 file
    """
    for file_path in files:
        tags = EasyMP3(file_path)
        tags.delete()
        tags.save()
