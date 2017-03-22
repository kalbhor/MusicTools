from musictools import musictools
from mutagen import File
import pytest
import os

songs_list = musictools.get_song_urls("Hey Jude")
url, file_name = songs_list[0]
artist, album, song_title, albumart = musictools.get_metadata("Hey Jude")
location = os.path.join('temp', file_name + '.mp3')

def test_get_song_urls():

    assert songs_list != None

def test_get_metadata():

    assert artist == 'The Beatles'
    assert album == '1 (Remastered)'

def test_download_song():

    musictools.download_song(url, 'temp/'+file_name)
    
    assert os.path.exists(location) == True

def test_add_albumart():

    musictools.add_albumart(location, albumart)
    tags = File(location)
 
    assert 'APIC:Cover' in tags.keys() != None

