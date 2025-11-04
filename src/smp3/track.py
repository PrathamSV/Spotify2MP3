from collections import namedtuple
from typing import Union, NamedTuple


class Track(namedtuple('TrackBase', ['id', 'name', 'artist', 'album', 'artwork'])):
    def __new__(cls, id: str, name: str, artist: str, album: str, artwork: str):
        return super().__new__(cls, id, name, artist, album, artwork)


class TDValue(NamedTuple):
    name: str
    artist: str
    album: str
    artwork: str


class TracksDict(dict):
    def __init__(self, *args, **kwargs: Union[TDValue, tuple[str, str, str, str]]):
        dict.__init__(self)
        self.update(*args, **kwargs)

    def __getitem__(self, key: str) -> str:
        return dict.__getitem__(self, key)

    def __setitem__(self, key: str, value: Union[TDValue, tuple[str, str, str, str]]):
        # Checks
        if not len(value) == 4:
            raise ValueError("Value must contain 4 arguments")
        for item in value:
            if not isinstance(item, str):
                raise TypeError("Values must be of type str")

        if isinstance(value, TDValue):
            dict.__setitem__(self, key, value)
        else:  # convert tuple to TDV
            dict.__setitem__(self, key, TDValue(name=value[0], artist=value[1], album=value[2], artwork=value[3]))

    def update(self, *args, **kwargs: Union[TDValue, tuple[str, str, str, str]]):
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def add_track(self, track: Track):
        self[track.id] = TDValue(name=track.name, artist=track.artist, album=track.album, artwork=track.artwork)
