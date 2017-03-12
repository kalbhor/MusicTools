#!/usr/bin/env python

import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
from os.path import splitext


def improve_name(song_name):
    """
    Improves file name by removing words such as HD, Official,etc
    eg : Hey Jude (Official HD) lyrics -> Hey Jude

    This helps in better searching of metadata since a spotify search of
    'Hey Jude (Official HD) lyrics' fetches 0 results
    """

    try:
        song_name = splitext(song_name)[0]
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


def img_search_google(album):
    """
    A simple method to return an image 
    given a query
    """

    album = album + " Album Art"
    url = ("https://www.google.com/search?q=" +
           quote(album.encode('utf-8')) + "&source=lnms&tbm=isch")
    header = {'User-Agent':
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/43.0.2357.134 Safari/537.36'
             }

    response = requests.get(url, headers=header)

    soup = BeautifulSoup(response.text, "html.parser")

    albumart_div = soup.find("div", {"class": "rg_meta"})
    albumart = json.loads(albumart_div.text)["ou"]

    return albumart

