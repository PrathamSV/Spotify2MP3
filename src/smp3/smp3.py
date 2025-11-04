import os
import re
import sys
import warnings
from contextlib import contextmanager
from pathlib import Path

import music_tag
import requests
import spotipy
from pydub import AudioSegment
from pytubefix import Search, exceptions
from spotipy.oauth2 import SpotifyClientCredentials
import json

# Local Imports
from .track import TracksDict, TDValue, Track
from .ProgressManager import ProgressManager, simple_bar


class Spotify2MP3:
    """
=================================================================================================================
Spotify2MP3 is a simple and easy Python module (and command-line utility) for downloading songs from Spotify.
Song metadata collected from Spotify is used to search YouTube and download.
-----------------------------------------------------------------------------------------------------------------
See https://developer.spotify.com/ for Spotify API, and information on how to obtain Client ID and Client Secret.
-----------------------------------------------------------------------------------------------------------------
Libraries used:
* spotipy: https://pypi.org/project/spotipy/
* pytubefix: https://pypi.org/project/pytubefix/
* pydub: https://pypi.org/project/pydub/
* music_tag: https://pypi.org/project/music_tag/
=================================================================================================================
    """

    def __init__(self, client_id: str, client_secret: str):
        """Creates spotipy object, and initates variables.

        Also See:
            * https://developer.spotify.com/dashboard/: to get client id and secret

        :param str client_id: Client ID from Spotify API
        :param str client_secret: Client Secret from Spotify API
        """
        self.cid = client_id
        self.secret = client_secret

        credentials = SpotifyClientCredentials(client_id=self.cid, client_secret=self.secret)
        self.sp = spotipy.Spotify(client_credentials_manager=credentials)
        self.dir = None
        self.img_dir = None
        self.search_lim = 5

    def get_track(self, track_id: str) -> Track:
        """Gets a track and its metadata from Spotify.

        Also See:
            * :py:class:`Track` for return type

        :param str track_id: ID/URI/URL of spotify track
        :return: Track obj with Id, Name, Artist, Album, and Artwork. ('ID', 'name', 'artist', 'album', 'artwork url')
        :rtype: Track
        """
        track_id = track_id.split('?si=')[0]
        track = self.sp.track(track_id=track_id)

        # Get Metadata
        id = track['id']
        name = track['name']
        artist = track['album']['artists'][0]['name']
        album = track['album']['name']
        artwork = track['album']['images'][0]['url']



        return Track(id=id, name=name, artist=artist, album=album, artwork=artwork)

    def get_playlist_tracks(self, playlist_id: str) -> TracksDict:
        """Gets tracks and their metadata from a Spotify playlist.

        Also See:
            * :py:class:`TracksDict` for return type

        :param str playlist_id: ID/URI/URL of spotify playlist
        :return: TracksDict obj with Id, Name, Artist, Album, and Artwork. {'ID': ('name', 'artist', 'album', 'artwork url') ...}
        :rtype: TracksDict
        """
        playlist_id = playlist_id.split('?si=')[0]
        output = TracksDict()
        # 'ID' : ('name', 'artist', 'album', 'artwork url')

        LIMIT = 100  # Only 100 songs can be fetched at once
        offset = 0
        tracks_found = 0
        print('Getting tracks...', end=' ')
        while True:
            # Track No.0-100, Track No.100-200 etc. Using offset to determine starting point.
            playlist_tracks = self.sp.playlist_items(playlist_id=playlist_id, offset=offset)["items"]
            count = 0
            for track in playlist_tracks:
                # Get metadata
                id = track["track"]["id"]
                name = track["track"]["name"]
                artist = track["track"]["album"]["artists"][0]["name"]
                album = track["track"]["album"]["name"]
                artwork = track['track']['album']['images'][0]['url']

                output[id] = TDValue(name=name, artist=artist, album=album, artwork=artwork)
                count += 1

            tracks_found += count

            if count < LIMIT:
                print(tracks_found,
                      'found')  # if inner loop breaks without reaching limit (100), then no more songs are left.
                break
            # else, more songs are available, so increase offset by limit (100) to fetch more tracks
            offset += LIMIT

        return output

    def get_album_tracks(self, album_id: str) -> TracksDict:
        """Gets tracks and their metadata from a Spotify album.

        Also See:
            * :py:class:`TracksDict` for return type

        :param str album_id: ID/URI/URL of spotify album
        :return: TracksDict obj with Id, Name, Artist, Album, and Artwork. {'ID': ('name', 'artist', 'album', 'artwork url') ...}
        :rtype: TracksDict
        """
        album_id = album_id.split('?si=')[0]
        output = TracksDict()
        # 'ID' : ('name', 'artist', 'album', 'artwork url')

        LIMIT = 50  # Only 50 songs can be fetched at once
        offset = 0
        tracks_found = 0
        print('Getting tracks...', end=' ')

        album_name = self.sp.album(album_id=album_id)["name"]

        while True:
            # Track No.0-50, Track No.50-100 etc. Using offset to determine starting point.
            album_tracks = self.sp.album_tracks(album_id=album_id, offset=offset)["items"]

            count = 0
            for track in album_tracks:
                # Get metadata
                id = track["id"]
                value = self.get_track(id)

                output[id] = TDValue(name=value.name, artist=value.artist, album=value.album, artwork=value.artwork)
                count += 1

            tracks_found += count

            if count < LIMIT:
                print(tracks_found,
                      'found')  # if inner loop breaks without reaching limit (50): then no more songs are left.
                break
            # else, more songs are available: so increase offset by limit (50) to fetch more tracks
            offset += LIMIT

        return output

    def get_user_tracks(self, user_id: str):
        """Gets playlist tracks and their metadata from a Spotify user.

        Also See:
            * :py:class:`TracksDict` for return type

        :param str user_id: ID/URI/URL of spotify user
        :return: TracksDict obj with Id, Name, Artist, Album, and Artwork. {'ID': ('name', 'artist', 'album', 'artwork url') ...}
        :rtype: TracksDict
        """
        user_id = user_id.split('?si=')[0]
        output = TracksDict()
        # 'ID' : ('name', 'artist', 'album', 'artwork url')

        LIMIT = 50  # Only 50 playlists can be fetched at once
        offset = 0
        playlists_found = 0
        print('Getting playlists...')

        while True:
            # Track No.0-50, Track No.50-100 etc. Using offset to determine starting point.
            user_playlists = self.sp.user_playlists(user=user_id, offset=offset)["items"]

            count = 0
            for playlist in user_playlists:
                # Get metadata
                print(f"Playlist {playlists_found + count + 1}.", end=' ')
                curr_playlist_tracks = self.get_playlist_tracks(playlist["id"])

                output.update(curr_playlist_tracks)
                count += 1

            playlists_found += count

            if count < LIMIT:
                print(playlists_found,
                      'playlists found.')  # if inner loop breaks without reaching limit (50): then no more songs are left.
                break
            # else, more songs are available: so increase offset by limit (50) to fetch more tracks
            offset += LIMIT

        return output

    def get_artist_tracks(self, artist_id):
        """Gets artists' tracks and their metadata from an artist.

        Also See:
            * :py:class:`TracksDict` for return type

        :param str artist_id: ID/URI/URL of spotify user
        :return: TracksDict obj with Id, Name, Artist, Album, and Artwork. {'ID': ('name', 'artist', 'album', 'artwork url') ...}
        :rtype: TracksDict
        """

        output = TracksDict()
        # 'ID' : ('name', 'artist', 'album', 'artwork url')

        LIMIT = 50  # Only 50 playlists can be fetched at once
        offset = 0
        albums_found = 0
        print('Getting playlists...')

        while True:
            # Track No.0-50, Track No.50-100 etc. Using offset to determine starting point.
            artist_albums = self.sp.artist_albums(artist_id=artist_id, offset=offset)["items"]

            count = 0
            for album in artist_albums:
                # Get metadata
                print(f"Album {albums_found + count + 1}.", end=' ')
                curr_album_tracks = self.get_album_tracks(album["id"])

                output.update(curr_album_tracks)
                count += 1

            albums_found += count

            if count < LIMIT:
                print(albums_found,
                      'albums found.')  # if inner loop breaks without reaching limit (50): then no more songs are left.
                break
            # else, more songs are available: so increase offset by limit (50) to fetch more tracks
            offset += LIMIT

        return output

    def save_track(self, track: Track, output_file: str, syntax: str = "'NAME' by ARTIST") -> None:
        """Saves all metadata of a track in a Track obj to file(*.txt).

        Also See:
            * :py:class:`Track` for parameter `track`.

        :param Track track: Track object containing metadata
        :param str output_file: Path to desired output file
        :param str syntax: Write syntax. Possible keywords: NAME, ARTIST, ALBUM, ID, ARTWORK
        """
        if not output_file[-4:] == ".txt":
            raise NameError("File should be a .txt")

        with open(output_file, 'a', encoding='utf-8') as file:
            output_str = syntax

            output_str = output_str.replace('ID', track.id)
            output_str = output_str.replace('NAME', track.name)
            output_str = output_str.replace('ARTIST', track.artist)
            output_str = output_str.replace('ALBUM', track.album)
            output_str = output_str.replace('ARTWORK', track.artwork)

            file.write(output_str)

        print("track saved:", track.name)

    def save_tracks(self, tracks: TracksDict, output_file: str, syntax: str = "'NAME' by ARTIST",
                    delim: str = '\n') -> None:
        """Saves metadata of all tracks in a TrackDict obj to file(*.txt).

        Also See:
            * :py:class:`TracksDict` for parameter `tracks`.

        :param TracksDict tracks: TracksDict object containing all metadata
        :param str output_file: Path to desired output file
        :param str syntax: Write syntax. Possible keywords: NAME, ARTIST, ALBUM, ID, ARTWORK
        :param str delim: Delimiter to separate entries
        """
        if not output_file[-4:] == ".txt":
            raise NameError("File should be a .txt")

        with open(output_file, 'a', encoding='utf-8') as file:
            for id, value in tracks.items():
                output_str = syntax

                output_str = output_str.replace("ID", id)
                output_str = output_str.replace("NAME", value.name)
                output_str = output_str.replace("ARTIST", value.artist)
                output_str = output_str.replace("ALBUM", value.album)
                output_str = output_str.replace("ARTWORK", value.artwork)

                file.write(output_str + delim)

        print(len(tracks), 'tracks saved successfully')

    def save_name(self, query: str, type: str, output_file: str) -> None:
        """Saves metadata of track/album/playlist/artist from name and type

        :param query: name
        :param type: options - track/album/playlist/artist
        :param output_file: output file location
        """

        result = self.sp.search(q=f'{type}:{query}', type=type, limit=self.search_lim)[type + "s"]["items"]
        i = 0

        while i < self.search_lim:
            try:
                print(f"{i + 1}: {result[i]['name']} 'BY' {result[i]['album']['artists'][0]['name']}")
                i += 1
            except IndexError:
                break

        if i < 1:
            print(f"No {type}s found")
            return
        else:
            ch = int(input("choice: ")) - 1

        result_id = result[ch]["id"]

        if type == 'track':
            data = self.get_track(result_id)
        elif type == 'playlist':
            data = self.get_playlist_tracks(result_id)
        elif type == 'album':
            data = self.get_album_tracks(result_id)
        elif type == 'artist':
            data = self.get_artist_tracks(result_id)
        else:
            raise ValueError("Incorrect Type")

        if type == 'track':
            self.save_track(track=data, output_file=output_file)
        else:
            self.save_tracks(tracks=data, output_file=output_file)

    def save_namelist(self, file_path: str, output_file: str, type: str, delim='\n'):
        """Saves metadata of track/album/playlist/artist from names in a file to a file

        :param file_path: location of track/album/playlist/artist list
        :param output_file: output file location
        :param type: options - track/album/playlist/artist
        :param delim: separator str for names in list
        :return: path to downloaded song
        :rtype: str | None
        """
        file = open(file_path).read()

        items = file.split(delim)

        failed = []

        for query in list(items):

            all_results = self.sp.search(q=f'{type}:{query}', type=type, limit=self.search_lim)[type + "s"]["items"]
            if len(all_results) < 1:
                failed.append(query)
                continue

            result = all_results[0]["id"]

            if type == 'track':
                data = self.get_track(result)
            elif type == 'playlist':
                data = self.get_playlist_tracks(result)
            elif type == 'album':
                data = self.get_album_tracks(result)
            elif type == 'artist':
                data = self.get_artist_tracks(result)
            else:
                raise ValueError("Incorrect Type")

            if type == 'track':
                self.save_track(track=data, output_file=utput_file)
            else:
                self.save_tracks(tracks=data, output_file=output_file)

        if len(failed) > 0:
            print("\nfailed: " + str(failed))

    def download_track(self, track: Track, search_syntax: str = 'ARTIST - NAME', with_artwork=True) -> str | None:
        """Downloads track from a Track obj. Searches YouTube for the songs and downloads them.

        Also See:
            * :py:class:`Track` for parameter track.

        :param Track track: Track object containing metadata
        :param str search_syntax: Syntax used to search YouTube. Possible keywords: NAME, ARTIST, ALBUM
        :return: Path to downloaded track
        :rtype: str | None
        """
        if self.dir is None:
            warnings.warn("Directory not set")
            return

        print("Download directory:", self.dir)

        query = search_syntax
        query = query.replace('NAME', track.name)
        query = query.replace('ARTIST', track.artist)
        query = query.replace('ALBUM', track.album)

        with self.__suppress_std():
            result = Search(query, 'WEB').results[0]
            stream = result.streams.filter(only_audio=True).order_by('abr').last()

        downloaded_path = stream.download(output_path=self.dir)

        downloaded_path = self.__single_to_mp3(downloaded_path, stream.abr)

        size = os.stat(downloaded_path).st_size / (1024 * 1024)

        if with_artwork:
            # download image
            img_data = requests.get(track.artwork).content
            artwork_name = f"Artist-{track.artist}_Album-{track.album}"
            artwork_name = re.sub(r'[/\:*?"<>|]', '_', artwork_name)  # noqa
            artwork_path = f"{self.img_dir}\\{artwork_name}.jpg"
            with open(artwork_path, "wb") as img:
                img.write(img_data)
            self.__add_metadata(file_path=downloaded_path, title=track.name, artist=track.artist, album=track.album,
                                artwork_local_path=artwork_path)
            size += os.stat(artwork_path).st_size / (1024 * 1024)
        else:
            self.__add_metadata(file_path=downloaded_path, title=track.name, artist=track.artist, album=track.album)

        print('Downloaded')
        print(str(round(size, 2)), 'MBs used')

        return downloaded_path


    def download_tracks(self, tracks: TracksDict, search_syntax: str = 'ARTIST - NAME', with_artwork: bool = True) -> list[str] | None:
        """Downloads all tracks from a TracksDict obj. Searches YouTube for tracks and downloads them.

        Also See:
            * :py:class:`TracksDict` for parameter tracks.

        :param TracksDict tracks: TracksDict object containing all metadata
        :param str search_syntax: Syntax used to search YouTube. Possible keywords: NAME, ARTIST, ALBUM
        :return: Paths to downloaded files
        :rtype: list[str] | None
        """
        if self.dir is None:
            warnings.warn("Directory not set")
            return

        space_used = 0

        print(f"Download directory: {self.dir}\n")

        download_paths = []

        progress = ProgressManager(tracks)

        for track in tracks.values():
            try:
                query = search_syntax
                query = query.replace('NAME', track.name)
                query = query.replace('ARTIST', track.artist)
                query = query.replace('ALBUM', track.album)

                progress.searching()

                with self.__suppress_std():

                    result = Search(query, 'WEB').results[0]

                stream = result.streams.filter(only_audio=True).order_by('abr').last()  # get stream

                progress.downloading()

                downloaded_path = stream.download(output_path=self.dir)  # download and store path

                progress.converting()

                downloaded_path = self.__single_to_mp3(downloaded_path, stream.abr)

                progress.downloaded()

                if with_artwork:
                    # download image
                    img_data = requests.get(track.artwork).content

                    artwork_name = f"Artist-{track.artist}_Album-{track.album}"
                    artwork_name = re.sub(r'[/\:*?"<>|]', '_', artwork_name)  # noqa
                    artwork_path = f"{self.img_dir}\\{artwork_name}.jpg"
                    if not os.path.exists(artwork_path):
                        with open(artwork_path, "wb") as img:
                            img.write(img_data)
                        space_used += os.stat(artwork_path).st_size / (1024 * 1024)

                    self.__add_metadata(file_path=downloaded_path, title=track.name, artist=track.artist,
                                        album=track.album,
                                        artwork_local_path=artwork_path)

                else:
                    self.__add_metadata(file_path=downloaded_path, title=track.name, artist=track.artist,
                                        album=track.album)

                progress.added_metadata()

                download_paths.append(downloaded_path)

                space_used += (os.stat(downloaded_path).st_size / (1024 * 1024))

            except exceptions.AgeRestrictedError:
                progress.error()

        errors = progress.completed()
        num_errors = len(errors)

        print(len(tracks) - num_errors, 'songs downloaded')
        print(str(round(space_used, 2)), 'MBs used\n')
        if num_errors > 0:
            print(f'{num_errors} tracks failed to download due to an Age Restriction on YouTube.\n{errors}')

        return download_paths

    def download_name(self, query: str, type: str, choice: bool = True, callback=None) -> str | None:
        """Download track/album/playlist/artist from name and type

        :param query: name of track/album/playlist/artist
        :param type: options - track/album/playlist/artist
        :param choice: confirm choice (out of top 5 results) in cmd
        :param callback: function to call after execution
        :return: path to downloaded song
        :rtype: str | None

        """

        result = self.sp.search(q=f'{type}:{query}', type=type, limit=self.search_lim)[type + "s"]["items"]


        if choice:
            i = 0
            while i < self.search_lim:
                try:
                    print(f"{i + 1}: {result[i]['name']} 'BY' {result[i]['album']['artists'][0]['name']}")
                    i += 1
                except IndexError:
                    break

            if i == 0:
                print(f"No {type}s found")
                if callback is not None:
                    callback()
                return

            else:
                ch = int(input("choice: ")) - 1
                result_id = result[ch]["id"]
        else:
            try:
                result_id = result[0]["id"]
            except IndexError:
                if callback is not None:
                    callback()
                return

        if type == 'track':
            data = self.get_track(result_id)
        elif type == 'playlist':
            data = self.get_playlist_tracks(result_id)
        elif type == 'album':
            data = self.get_album_tracks(result_id)
        elif type == 'artist':
            data = self.get_artist_tracks(result_id)
        else:
            raise ValueError('Incorrect Type')

        if type == 'track':
            path = self.download_track(data)
        else:
            path = self.download_tracks(data)

        if callback is not None:
            callback()

        return path

    # TODO: Include CSVs
    def download_namelist(self, file_path: str, type: str, delim='\n'):
        """Download track/album/playlist/artist from names in a file

        :param file_path: location of track/album/playlist/artist list
        :param type: options - track/album/playlist/artist
        :param delim: separator str for names in list
        :return: path to downloaded song
        :rtype: str | None

        """
        file = open(file_path).read()

        items = file.split(delim)

        paths = []
        failed = []
        count = 0


        for query in list(items):
            if not query:
                continue

            all_results = self.sp.search(q=f'{type}:{query}', type=type, limit=self.search_lim)[type + "s"]["items"]
            if len(all_results) < 1:
                failed.append(query)
                items.remove(query)
                continue

            result = all_results[0]["id"]

            simple_bar(max_count=len(items), count=count, msg=f'fetching data for {query}')

            if type == 'track':
                data = self.get_track(result)
            elif type == 'playlist':
                data = self.get_playlist_tracks(result)
            elif type == 'album':
                data = self.get_album_tracks(result)
            elif type == 'artist':
                data = self.get_artist_tracks(result)
            else:
                raise ValueError("Incorrect Type")

            simple_bar(max_count=len(items), count=count, msg=f'downloading {query}')

            with self.__suppress_std():
                if type == 'track':
                    path = self.download_track(data)
                else:
                    path = self.download_tracks(data)

            count += 1

            simple_bar(max_count=len(items), count=count, msg=f'downloaded {query}')

            paths.append(path)

        if len(failed) > 0:
            print("\nfailed: " + str(failed))
        return paths

    def set_dir(self, dir: str) -> None:
        """Sets download directory.

        :param str dir: Path to download directory
        """
        self.dir = dir
        self.img_dir = dir + "\\Artwork"
        if not os.path.exists(self.img_dir):
            os.mkdir(self.img_dir)

    def get_dir(self) -> str:
        """Returns download directory.

        :return: download directory
        :rtype: str
        """
        return self.dir

    def webm_to_mp3(self, check_subfolders: bool = True) -> list[str] | None:
        """Converts .webm files to .mp3[s].

        :param bool check_subfolders: If subfolders should be searched for .webm[s]
        :return: Paths to mp3 files
        :rtype: list[str]
        """
        if self.dir is None:
            System.out.println("Directory not set")
            return

        file_list = []

        if check_subfolders:
            for file in Path(self.dir).rglob('*.webm'):
                file_list.append(file.__str__())
        else:
            for file in Path(self.dir).glob('*.webm'):
                file_list.append(file.__str__())

        file_list_len = len(file_list)
        print('Converting...')

        mp3_paths = []
        count = 0
        for webm_path in file_list:
            simple_bar(max_count=file_list_len, count=count,
                                msg='Converting ' + webm_path.replace(self.dir + r''"\\", ''))

            mp3_path = webm_path.replace('.webm', '.mp3')
            AudioSegment.from_file(webm_path).export(mp3_path, format='mp3')
            os.remove(webm_path)

            simple_bar(max_count=file_list_len, count=count,
                                msg=mp3_path)

            count += 1
            mp3_paths.append(mp3_path)

        simple_bar(max_count=file_list_len, count=count, msg='Completed\n')

        return mp3_paths

    def __single_to_mp3(self, path: str, abr):
        new_path = path.split('.')
        new_path.pop()
        new_path = '.'.join(new_path) + ".mp3"

        AudioSegment.from_file(path).export(new_path, format='mp3',
                                            parameters=['-acodec', 'libmp3lame', '-abr', 'true', '-b:a', abr[:-3:]])
        os.remove(path)

        return new_path


    def __add_metadata(self, file_path: str, title: str, artist: str, album: str, artwork_local_path: str = None):
        f = music_tag.load_file(file_path)
        f['title'] = title
        f['artist'] = artist
        f['album'] = album
        if artwork_local_path is not None:
            with open(artwork_local_path, 'rb') as img:
                f['artwork'] = img.read()
                f['artwork'].first.thumbnail([512, 512])
        f.save()


    @contextmanager
    def __suppress_std(self) -> None:
        """Supresses StdOut and StdErr.
        Because some modules output too much to the terminal
        """
        with open(os.devnull, "w") as null:
            org_stdout = sys.stdout
            org_stderr = sys.stderr

            sys.stdout = null
            sys.stderr = null
            try:
                yield
            finally:
                sys.stdout = org_stdout
                sys.stderr = org_stderr
