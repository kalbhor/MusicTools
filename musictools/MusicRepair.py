
import requests
import spotipy
from mutagen.id3 import ID3, APIC, _util
from mutagen.mp3 import EasyMP3
from bs4 import BeautifulSoup
from urllib.request import urlopen
from .improve import improve_name, img_search_google


class MusicRepair(object):
    """
    Adds album art, album name, title, artist,etc
    to a .mp3 file
    """

    def __init__(self):
        pass

    @staticmethod
    def get_details_spotify(file_name):
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

            return artist, album, song_title, albumart, ''

        except Exception as error:
            return ' ', ' ', song_name, None, error

    @staticmethod
    def add_albumart(file_name, song_title=None, albumart=None):
        """
        Add albumart in .mp3's tags
        """

        if albumart is None:
            albumart = img_search_google(song_title)
        else:
            pass
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
        """
        As the method name suggests
        """
        tags = EasyMP3(file_name)
        tags["title"] = title
        tags["artist"] = artist
        tags["album"] = album
        tags.save()
