from itertools import chain
from os import path
from pathlib import Path
import music_tag

def find_duplicates(*paths, file_extensions=('*.mp3', '*.wav')):

    all_files = []
    duplicate_paths = []

    for file_path in __path_handler(*paths, file_extensions=file_extensions):
        f = music_tag.load_file(file_path)
        track_repr = (str(f['title']), str(f['artist']))

        if track_repr in all_files:
            duplicate_paths.append(str(file_path))
        else:
            all_files.append(track_repr)

    return duplicate_paths

def __path_handler(*paths, file_extensions):
    out = iter(())
    for path in paths:
        for ext in file_extensions:
            pathlist = Path(path).rglob(ext)
            out = chain(out, pathlist)
    return out
