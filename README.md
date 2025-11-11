# Spotify2MP3

Spotify2MP3 is a simple and easy Python module (and command-line utility) for downloading songs from Spotify.
Song metadata collected from Spotify is used to search YouTube and download.

<br><br>

## Module Usage

1. <b>Setup Spotify API</b><br>
   Visit the Spotify developer [website](https://developer.spotify.com/) to obtain Client ID and Secret.
   
3. <b>Install requirements</b><br>
   Navigate to Spotify2MP3 folder and run:
   ```sh
   pip install -r requirements.txt
   ```

4. <b>Import package</b>
   ```py
   from smp3 import Spotify2MP3
   ```

#### Example script
```py
from os import path
from smp3 import Spotify2MP3

download_dir = path.join(path.expanduser('~'), 'Music', 'Spotify2MP3')
list_path = path.join(path1, 'songs.txt')

client_id = ''
client_secret = ''

s = Spotify2MP3(client_id=client_id, client_secret=client_secret)
s.set_dir(download_dir)

s.download_namelist(file_path=list_path, type='track')
```
<br><br>
## CLI Usage

1. <b>Setup Spotify API</b><br>
   Visit the Spotify developer [website](https://developer.spotify.com/) to obtain Client ID and Secret.

3. <b>Add package-level constants</b><br>
   Add obtained Spotify Client ID and Secret to [\_\_init\_\_.py](/smp3/__init__.py)

5. <b>Run CLI</b><br>
   Navigate to Spotify2MP3 folder and run:
   ```sh
   py cli.py -h
   ```

### Example commands
```sh
py cli.py -n "Night Running" track -d
```
```sh
py cli.py -i "6lRU3pKjNnSI9svHzznkC6" track -d
```
```sh
py cli.py -i "https://open.spotify.com/album/2x6LWti2bjYS6AllSomoV7" album -s
```
```sh
py cli.py -nl "songs.txt" track -d
```
<br>

> This is an old project of mine that I ported over to GitHub
