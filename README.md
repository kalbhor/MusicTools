<h2> M U S I C &nbsp; T O O L S </h2>
[![Build Status](https://travis-ci.org/lakshaykalbhor/MusicTools.svg?branch=master)](https://travis-ci.org/lakshaykalbhor/MusicTools)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)](LICENSE)

#### Library to download, sort and tag music files

## Social:

[![GitHub stars](https://img.shields.io/github/stars/lakshaykalbhor/musictools.svg?style=social&label=Star)](https://github.com/lakshaykalbhor/musictools)
[![GitHub followers](https://img.shields.io/github/followers/lakshaykalbhor.svg?style=social&label=Follow)](https://github.com/lakshaykalbhor)  
[![Twitter Follow](https://img.shields.io/twitter/follow/lakshaykalbhor.svg?style=social)](https://twitter.com/lakshaykalbhor)

## Installing

#### From Source:

```sh
$ git clone https://github.com/lakshaykalbhor/MusicTools
$ cd MusicTools
$ python setup.py install
```

#### From PyPI:
```sh
$ pip install musictools
```
<br>

## Methods

##### Provides a list of youtube videos of the song with urls and titles
```
musictools.get_song_urls(song_name)
```

##### Download song from youtube, optionally provide directory to download to.
```
musictools.download_song(song_url, song_title, dl_directory)
```

##### Provides artist name, song name, album name and album art for a particular song
```
musictools.get_metadata(file_name) 
```

##### Adds an image as the album art of a mp3 file
```
musictools.add_albumart(file_name, song_title, albumart)
```

##### Adds title, artist and album name in a mp3 file

```
musictools.add_metadata(file_name, title, artist, album)
```

## Example
```sh

>>> from musictools import musictools

>>> songs_list = musictools.get_song_urls("Hey Jude")
>>> print(songs_list[0])
('https://www.youtube.com/watch?v=A_MjCqQoLLA', 'The Beatles - Hey Jude')

>>> url, title = songs_list[0]
>>> print(url)
https://www.youtube.com/watch?v=A_MjCqQoLLA
>>> print(title)
The Beatles - Hey Jude

>>> musictools.download_song(url, title, dl_directory='~/Desktop/Music/')

>>> musictools.get_metadata(title)
('The Beatles', '1 (Remastered)', 'Hey Jude - Remastered 2015', 'https://i.scdn.co/image/9ecfdf528562cae879748b73bd81b64dfa3d5704')

>>> artist, album , song_name, albumart = musictools.get_metadata(title)

>>> musictools.add_albumart(title, song_name, albumart)
>>> musictools.add_metadata(title, song_name, artist, album)

```



## Contributing
Currently this project is in its infancy and issues are bound to arise.
To contribute, [post issues](https://github.com/lakshaykalbhor/MusicTools/issues) without hesitation and [open pull requests](https://github.com/lakshaykalbhor/MusicTools/pulls) to add/improve features.

## License 
#### [MIT](https://github.com/lakshaykalbhor/MusicTools/blob/master/LICENSE)

