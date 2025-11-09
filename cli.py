import argparse
from os.path import exists, isdir, isfile
# Local
from smp3 import Spotify2MP3, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SAVE_PATH, DOWNLOAD_PATH

parser = argparse.ArgumentParser(description="""Spotify2MP3 is a simple and easy Python module and (command-line utility) for downloading songs from Spotify.
Song metadata collected from Spotify is used to search YouTube and download audio.""", formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('type', metavar='type', type=str, choices=['track', 'playlist', 'album', 'user', 'artist'], help='Type. Choices: track, playlist, album, user, artist')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-i', '--id', metavar='id', type=str, help='Spotify ID/URI/URL')
group.add_argument('-n', '--name', metavar='name', type=str, help='Name of Track/Playlist/Album/Artist')
group.add_argument('-nl', '--namelist', metavar='namelist', type=str, help='location of file with list of Track/Playlist/Album/Artist')

group2 = parser.add_mutually_exclusive_group(required=True)
group2.add_argument('-s', '--save', metavar='save', help='*.txt file to save song metadata, leave value empty if set in __init__', nargs='?', const=True)
group2.add_argument('-d', '--download', metavar='download', help='Path/folder to download tracks, leave value empty if set in __init__', nargs='?', const=True)


args = parser.parse_args()


def save(s, savefile):
    if args.name is not None:
        s.save_name(query=args.name, type=args.type, output_file=savefile)
    elif args.namelist is not None:
        s.save_namelist(file_path=args.namelist, type=args.type, output_file=savefile)
    else:
        if args.type == 'track':
            track = s.get_track(track_id=args.id)
            s.save_track(track=track, output_file=savefile)
        elif args.type == 'playlist':
            playlist = s.get_playlist_tracks(playlist_id=args.id)
            s.save_tracks(tracks=playlist, output_file=savefile)
        elif args.type == 'album':
            album = s.get_album_tracks(album_id=args.id)
            s.save_tracks(tracks=album, output_file=savefile)
        elif args.type == 'user':
            user = s.get_user_tracks(user_id=args.id)
            s.save_tracks(tracks=user, output_file=savefile)
        elif args.type == 'artist':
            artist = s.get_artist_tracks(artist_id=args.id)
            s.save_tracks(tracks=artist, output_file=savefile)



def download(s, downloadpath):
    s.set_dir(dir=downloadpath)
    if args.name is not None:
        s.download_name(query=args.name, type=args.type)
    elif args.namelist is not None:
        s.download_namelist(file_path=args.namelist, type=args.type)
    else:
        if args.type == 'track':
            track = s.get_track(track_id=args.id)
            s.download_track(track=track)
        elif args.type == 'playlist':
            playlist = s.get_playlist_tracks(playlist_id=args.id)
            s.download_tracks(tracks=playlist)
        elif args.type == 'album':
            album = s.get_album_tracks(album_id=args.id)
            s.download_tracks(tracks=album)
        elif args.type == 'user':
            user = s.get_user_tracks(user_id=args.id)
            s.download_tracks(tracks=user)



if args.type == 'user' and args.name is not None:
    raise TypeError("Cannot get user tracks with user's name")

if args.save:
    if args.save == True:
        savefile = SAVE_PATH
    else:
        savefile == args.save

    if not isinstance(savefile, str):
        raise ValueError("Save file must be a str type")
    elif not exists(savefile):
        raise FileNotFoundError("Save file does not exist.")
    elif not isfile(savefile):
        raise ValueError("Provided path is not a file")
    else:
        s = Spotify2MP3(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        save(s, savefile)

elif args.download:
    if args.download == True:
        downloadpath = DOWNLOAD_PATH
    else:
        downloadpath = args.download

    if not isinstance(downloadpath, str):
        raise ValueError("Download path must be a str type")
    elif not exists(downloadpath):
        raise FileNotFoundError("Download directory does not exist.")
    elif not isdir(downloadpath):
        raise ValueError("Provided path is not a directory")
    else:
        s = Spotify2MP3(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        download(s, downloadpath)


