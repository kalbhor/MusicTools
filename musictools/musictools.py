#!/usr/bin/env python

import requests
import youtube_dl
import spotipy
import os
import re
from mutagen.id3 import ID3, APIC, _util
from mutagen.mp3 import EasyMP3
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

# Words to omit from song title for better results through spotify's API
chars_filter = "()[]{}-:_/=+\"\'"
words_filter = ('official', 'lyrics', 'audio', 'remixed', 'remix', 'video',
                'full', 'version', 'music', 'mp3', 'hd', 'hq', 'uploaded', 'explicit')

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
        'postprocessors': [
            {'key': 'FFmpegExtractAudio','preferredcodec': 'mp3',
             'preferredquality': '192',
            },
            {'key': 'FFmpegMetadata'},
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(song_url, download=True)


def get_metadata(file_name, client_id, client_secret):
    """
    Tries finding metadata through Spotify
    """

    song_name = improve_name(file_name)  # Remove useless words from title
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)

    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = spotify.search(song_name, limit=1)

    results = results['tracks']['items'][0]  # Find top result
    album = results['album']['name']  # Parse json dictionary
    artist = results['album']['artists'][0]['name']
    song_title = results['name']
    album_art = results['album']['images'][0]['url']

    return artist, album, song_title, album_art


def add_album_art(file_name, album_art):
    """
    Add album_art in .mp3's tags
    """

    img = requests.get(album_art, stream=True)  # Gets album art from url
    img = img.raw

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

    return album_art


def add_metadata(file_name, title, artist, album):
    """
    As the method name suggests
    """
    
    tags = EasyMP3(file_name)
    if title: 
        tags["title"] = title
    if artist:     
        tags["artist"] = artist
    if album:
        tags["album"] = album
    tags.save()

    return file_name

def get_current_metadata_tag(file_name, tag):
    tags = EasyMP3(file_name)
    if tag in tags:
        return tags[tag].pop()
    else:
        return "The metadata tag could not be found."


def revert_metadata(files):
    """
    Removes all tags from a mp3 file
    """
    for file_path in files:
        tags = EasyMP3(file_path)
        tags.delete()
        tags.save()
