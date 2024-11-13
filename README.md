# troja

[**bis Troja brennt!**](https://open.spotify.com/track/5IE8RYLIjM4oy5Cr3Q3RQy?si=899fa3fb471f46cb)

spotify CLI client

- play specific song, playlist or album
- pause or skip song
- see your spotify stats (most played artist/tracks)
- create a new playlist, manually adding song or getting automatic recommendations by specifying artists, genres or similar songs
- expand existing playlist with new songs
- some more stuff!!



uses [spotipy 2.24.0](https://spotipy.readthedocs.io/en/2.24.0/) for API stuff

currently only in galician


<details>
<summary>installation</summary>

1. clone the repository:
   ```bash
   git clone https://github.com/manu-pc/troja.git
   cd troja

2. install all dependencies
    * if your python environment is externally managed (ex: ubuntu) you'll need to setup a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

</details>

<details>
<summary>setup</summary>

1. get a key
    to run you'll need to setup a file with a <ins>client id</ins>, <ins>secret id</ins> and <ins>redirect url</ins>, which you can easily get [here](https://developer.spotify.com/documentation/web-api)

2. create a config.ini file. it should look like:
    ```ini
    [SPOTIPY]
    client_id = your_spotify_client_id
    client_secret = your_spotify_client_secret
    redirect_uri = your_redirect_uri

    
<details>