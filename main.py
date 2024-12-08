# bis Troja brennt!

import spotipy  # https://spotipy.readthedocs.io/en/2.24.0/
import time
import random
import difflib
import sys
from spotipy.oauth2 import SpotifyOAuth
import configparser

# - - - - VARIABLES - - - - #
ranges = ["short_term", "medium_term", "long_term"]
MAX_QUEUE = 5
playlists = []
playlist_names = []
top_artists = {"short_term": [], "medium_term": [], "long_term": []}
top_tracks = {"short_term": [], "medium_term": [], "long_term": []}
colors = {
    "blue": "\u001B[34m",
    "light_red": "\u001B[31m",
    "purple": "\u001B[35m",
    "yellow": "\u001B[33m",
    "white": "\u001B[37m",
    "green": "\u001B[32m",
    "cyan": "\u001B[36m",
    "magenta": "\u001B[35m",
    "black": "\u001B[30m",
    "grey": "\u001B[90m",
    "light_red": "\u001B[91m",
    "light_green": "\u001B[92m",
    "light_yellow": "\u001B[93m",
    "light_blue": "\u001B[94m",
    "light_magenta": "\u001B[95m",
    "light_cyan": "\u001B[96m",
    "light_white": "\u001B[97m",
    "reset": "\u001B[0m",
}
scope = [
    "user-library-read",
    "user-read-playback-state",
    "user-modify-playback-state",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-top-read",
    "playlist-read-private",
]
# https://developer.spotify.com/documentation/web-api/concepts/scopes


# - - - - FUNCIÓNS - - - - #
def printc(text, color="white", newline=True):  # imprime en cor
    try:
        if newline:
            print(colors[color] + text + colors["reset"])
        else:
            print(colors[color] + text + colors["reset"], end="")
    except TypeError:
        print(text)


def intput(prompt, min=0, max=9999):
    ans = None
    while ans is None:
        try:
            ans = int(input(prompt))
            if not min <= ans <= max:  # If outside the range, reset ans to None
                printc(
                    "Invalid number, must be between "
                    + str(min)
                    + " and "
                    + str(max)
                    + ".",
                    "light_red",
                )
                ans = None
        except ValueError:
            printc("Please enter a number.", "light_red")
            ans = None
    return ans


def fullname(track):
    return track["name"] + " - " + track["artists"][0]["name"]


def now_playing():
    try:
        playback = sp.current_playback()
        if playback and playback["is_playing"]:
            track = playback["item"]
            printc("Now playing: ", newline=False)
            printc(track["name"], color=song_color, newline=False)
            printc(" - ", color="grey", newline=False)
            printc(track["artists"][0]["name"], color=artist_color)
    except Exception:
        printc(
            "[W] No active playback found! Please start playing spotify on a device to begin.",
            "yellow",
        )


def skip(silent=False):
    sp.next_track(device_id=None)
    if not silent:
        time.sleep(0.6)
        now_playing()


def play(playlist):
    try:
        if playlist["type"] == "album":
            sp.shuffle(state=False)
            printc("Playing album: ", newline=False)
            printc(playlist["name"], album_color, newline=False)
            printc(" - ", "grey", newline=False)
            printc(playlist["artists"][0]["name"], artist_color)
        else:
            printc("Playing playlist: ", newline=False)
            printc(playlist["name"], playlist_color, newline=False)
            if playlist["description"] != "":
                printc(" (" + playlist["description"] + ") ")
            else:
                print("\n")
            sp.shuffle(state=True)
        sp.start_playback(context_uri=playlist["uri"])
        time.sleep(0.7)
        now_playing()
    except Exception:
        printc(
            "No active playback found. Please start playing spotify on a device to begin.",
            "light_red",
        )


def p(query, silent=False):  # plays a song w/o interrupting queue
    song = sp.search(q=query, limit=5, type="track")["tracks"]["items"][0]
    sp.add_to_queue(song["external_urls"]["spotify"])
    skip(silent)


def queue_uri(n):  # lee o uri dos n proximos da cola
    q_uri = []
    for k in range(n):
        q_uri += [sp.queue()["queue"][k]["uri"]]
    return q_uri

def load_devices():
    global devices
    devices = sp.devices()["devices"]
    printc(f"Loaded {len(devices)} devices.", "green")

def load_playlists():
    global playlist_names, playlists

    # Spotify authentication

    # Get current user's playlists
    user_playlists = sp.current_user_playlists()

    while user_playlists:
        for playlist in user_playlists['items']:
            # Append playlist name and playlist object to the global arrays
            if playlist is None:
                continue
            playlist_names.append(playlist['name'])
            playlists.append(playlist)
        if user_playlists['next'] is not None:
            user_playlists = sp.next(user_playlists)
        else:
            break

def create_top_playlist(n, time_range):
    tempos = {
        "short_term": " this month",
        "medium_term": " last 6 months",
        "long_term": "",
    }
    p_name = "top " + str(n) + tempos[time_range] + " de " + username
    p_desc = "Created with troja"
    play_id = sp.user_playlist_create(user_id, name=p_name, description=p_desc)["uri"]

    song_list = top_tracks[time_range][:n]
    k = 0
    for song in song_list:
        song_list[k] = song["uri"]
        k += 1

    sp.playlist_add_items(playlist_id=play_id, items=song_list)

    return play_id


#!DEPRECATED
def expand_playlist(
    play_id, seed_artists=None, seed_tracks=None, seed_genres=None, limit=50
):
    try:
        recommendations = sp.recommendations(
            seed_artists=seed_artists,
            seed_tracks=seed_tracks,
            seed_genres=seed_genres,
            limit=limit,
        )
        newsongs = [track["uri"] for track in recommendations["tracks"]]
        sp.playlist_add_items(playlist_id=play_id, items=newsongs)
        printc(f"Successfully added {len(newsongs)} songs to the playlist.", "green")
    except Exception as e:
        report(e)


def init():
    print("Welcome, " + username + "!", end="")
    printc(" [ID: " + user_id + "]", "yellow")
    print("Loading playlists... ", end="")
    load_playlists()
    print("Loading devices... ", end="")
    load_devices()
    now_playing()
    printc("Type 'help' to see a list of valid commands.")


def report(error):
    printc("An error occurred. (" + str(error) + ")", "light_red")


def load_top():
    global top_artists
    global top_tracks

    for time_range in ranges:
        top_artists[time_range] += sp.current_user_top_artists(
            limit=50, time_range=time_range
        )["items"]
        top_tracks[time_range] += sp.current_user_top_tracks(
            limit=50, time_range=time_range
        )["items"]


# - - - - INIT - - - - #
config = configparser.ConfigParser()
try:
    configModified = False
    config.read("config.ini")
    client_id = config.get("SPOTIPY", "client_id")
    client_secret = config.get("SPOTIPY", "client_secret")
    redirect_uri = config.get("SPOTIPY", "redirect_uri")
    # Check if colors section exists, if not, create it
    if not config.has_section("COLORS"):
        config.add_section("COLORS")
        printc(
            "[Tip]: you can change colors by modifying the config.ini file! This message appeared because no colors were found.",
            color="yellow",
        )
        configModified = True

    if not config.has_option("COLORS", "song_color"):
        config.set("COLORS", "song_color", "blue")
    if not config.has_option("COLORS", "artist_color"):
        config.set("COLORS", "artist_color", "purple")
    if not config.has_option("COLORS", "album_color"):
        config.set("COLORS", "album_color", "green")
    if not config.has_option("COLORS", "playlist_color"):
        config.set("COLORS", "playlist_color", "yellow")
    if not config.has_option("COLORS", "user_color"):
        config.set("COLORS", "user_color", "light_cyan")

    if configModified:
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    song_color = config.get("COLORS", "song_color")
    artist_color = config.get("COLORS", "artist_color")
    album_color = config.get("COLORS", "album_color")
    playlist_color = config.get("COLORS", "playlist_color")
    user_color = config.get("COLORS", "user_color")
    # Validate colors
    default_color = "white"
    for color_key in [
        "song_color",
        "artist_color",
        "album_color",
        "playlist_color",
        "user_color",
    ]:
        if config.get("COLORS", color_key) not in colors:
            printc(
                f"[W] {color_key} is not a valid color. Replacing with default color.",
                "yellow",
            )
            config.set("COLORS", color_key, default_color)
            configModified = True

    if configModified:
        with open("config.ini", "w") as configfile:
            config.write(configfile)

except Exception:
    printc(
        "config.ini file couldn't be read! please check setup instructions on the readme.md file.",
        "light_red",
    )
    sys.exit(1)


print("Logging in...", end="")
try:
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
    )
except Exception as e:
    printc("Couldn't log in!")
    report(e)
    sp = None
    sys.exit(1)
printc(" Success!", "light_green")

try:
    username = sp.me()["display_name"]
    user_id = sp.me()["id"]
    query = ""
    init()

except Exception as e:
    printc(
        "an error occurred while initializing!! even though the login was successful! which is weird!!!"
    )
    report(e)
    sys.exit(1)

inp = ""
warn_time = True

# - - - - MAIN LOOP - - - - #
while inp != "/":
    inp = input(colors[user_color] + "\n<" + username + ">: " + colors["reset"])

    # - - - - HELP - - - - #
    if inp == "help":
        printc(
            "/ - exit the program\n"
            "q (+ song) - check current queue, or add song to queue \n"
            "s, skip - skip current song\n"
            "p + song - start playing a song, without modifying the queue\n"
            "play + playlist - start playing a playlist\n"
            "aplay + album - start playing an album\n"
            "save + playlist - add the current song to a playlist \n"
            "t, top - check most listened songs/artists, and allows exporting them to a playlist\n"
            "make - create a playlist, manually or auto-completed with Spotify algorithm\n"
            "reroll - randomize the current queue\n"
        )

    #if inp == "help+":
    #    printc(
            #"expand + playlist - expand an existing playlist with recommendations\n"
            #"rec - start playing a random recommendation, based on your current queue\n"
            #"rec + artist - start playing a random recommendation from an artist \n"
            #"d, discover - recommend new songs, albums, or artists \n"
            #"(include a + after the artist name to allow similar artists)"
    #    )

    # - - - - PLAYBACK - - - - #
    if inp == "q":  # Q - IMPRIMIR COLA
        now_playing()
        printc("Current queue:")
        i = 0
        for track in sp.queue()["queue"]:
            if i < MAX_QUEUE:
                printc("\n - " + fullname(track))
            i += 1

    if inp.startswith("q "):  # Q + CANCIÓN  -  ENGADIR CANCIÓN A COLA
        query = inp.split("q ")[1]

        try:
            song = sp.search(q=query, limit=1, type="track")["tracks"]["items"][0]
            sp.add_to_queue(song["external_urls"]["spotify"])

            printc("Added to queue:")
            printc(fullname(song))
        except Exception as e:
            report(e)

    if inp == "p":
        if sp.current_playback()["is_playing"]:
            printc("Pausing playback...")
            sp.pause_playback()

        else:
            try:
                sp.start_playback()
                now_playing()

            except Exception as e:
                report(e)

    if inp.startswith("p "):  # P + CANCIÓN  -  ENGADIR CANCIÓN A COLA E REPRODUCILA
        query = inp.split("p ")[1]

        try:
            p(query)

        except Exception as e:
            report(e)

    if inp.startswith("config"):
        try:
            parts = inp.split()
            if len(parts) == 3 and parts[1] in [
                "song_color",
                "artist_color",
                "album_color",
                "playlist_color",
                "user_color",
            ]:
                color_key = parts[1]
                new_color = parts[2]
                if new_color in colors:
                    config.set("COLORS", color_key, new_color)
                    with open("config.ini", "w") as configfile:
                        config.write(configfile)
                    printc(f"{color_key} has been updated to {new_color}.", "green")
                    globals()[color_key] = new_color
                else:
                    printc(f"{new_color} is not a valid color.", "light_red")
            else:
                printc("Usage: config [color_key] [color]", "yellow")
        except Exception as e:
            report(e)

    if inp == "play":
        printc("Saved playlists: ")
        printc(playlist_names)
        printc("Use play [playlist] to start playing a playlist.")

    if inp.startswith("save "):  # SAVE + PLAYLIST  -  GARDA A PLAYLIST
        query = inp.split("save ")[1]
        try:
            matches = difflib.get_close_matches(query, playlist_names, n=1, cutoff=0.6)
            if matches:  # check if there are any matches
                p_name = matches[0]
                playlist = playlists[playlist_names.index(p_name)]
                song = sp.currently_playing()["item"]
                sp.playlist_add_items(playlist["uri"], [song["uri"]])
                printc("Added ", newline=False)
                printc(song["name"], song_color, newline=False)
                printc(" - ", newline=False)
                printc(song["artists"][0]["name"], artist_color, newline=False)
                printc(" to ", newline=False)
                printc(p_name, playlist_color, newline=False)
                printc(".")
            else:
                printc("Playlist not found! please try again.", "light_red")
        except Exception as e:
            report(e)

    if inp.startswith("aplay "):  # APLAY + ALBUM  -  REPRODUCIR ÁLBUM
        query = inp.split("aplay ")[1]
        try:
            playlist = sp.search(q=query, limit=1, type="album")["albums"]["items"][0]
            play(playlist)

        except Exception as e:
            report(e)
    if inp.startswith("play "):  # PLAY + PLAYLIST  -  REPRODUCIR PLAYLIST GARDADA
        query = inp.split("play ")[1]
        match = difflib.get_close_matches(query, playlist_names, n=1, cutoff=0.6)
        if not match:
            match = difflib.get_close_matches(
                query.upper(), playlist_names, n=1, cutoff=0.6
            )

        if match:
            # se hai unha parecida
            playlist_name = match[0]
            try:
                playlist = playlists[playlist_names.index(playlist_name)]
                play(playlist)
            except Exception as e:
                printc("Couldn't load playlist " + playlist_name + ".", "light_red")
        else:
            # se non encontra ningunha playlist parecido ao que buscas, pide:
            inp = input(
                f'Couldn\'t find playlist "{query}".\n'
                "0 - cancel\n"
                "1 - search online\n"
                "2 - search albums\n"
                "<" + username + ">: "
            )
            if inp == "1":
                playlist = sp.search(q=query, limit=1, type="playlist")["playlists"][
                    "items"
                ][0]
                play(playlist)
            elif inp == "2":
                printc("Tip: you can also use aplay [album]")
                playlist = sp.search(q=query, limit=1, type="album")["albums"]["items"][
                    0
                ]
                play(playlist)
    if inp in ["skip", "s"]:  # S -  SALTAR CANCIÓN
        try:
            skip()
        except Exception as e:
            report(e)

    if inp == "rec":  # REC - REPRODUCIR RECOMENDACIÓN
        printc("This feature has been deprecated due to changes to Spotify's API. You can read more here: "
               +"https://community.spotify.com/t5/Spotify-for-Developers/Changes-to-Web-API/td-p/6540414" +
               "\nSorry for the inconvenience :(", "light_red")
        continue
        try:
            song = sp.recommendations(seed_tracks=(queue_uri(5)), limit=1)["tracks"][0]
            sp.add_to_queue(song["external_urls"]["spotify"])
            skip()
        except Exception as e:
            report(e)
            report(e)

    if inp.startswith("rec "):
        printc("This feature has been deprecated due to changes to Spotify's API. You can read more here: "
               +"https://community.spotify.com/t5/Spotify-for-Developers/Changes-to-Web-API/td-p/6540414" +
               "\nSorry for the inconvenience :(", "light_red")
        continue
        inp = inp.split("rec ")[1]
        artist = sp.search(q=inp, limit=5, type="artist")["artists"]["items"][0]
        song = sp.recommendations(seed_artists=[artist["uri"]], limit=1)["tracks"][0]
        if not inp.endswith("+") and warn_time:  # este aviso solo salta unha vez
            printc(
                "This could take a while because of how Spotify's algorithm works..."
            )
            warn_time = False
        while (song["artists"][0]["name"] != artist["name"]) and not inp.endswith("+"):
            song = sp.recommendations(seed_artists=[artist["uri"]], limit=1)["tracks"][
                0
            ]

        sp.add_to_queue(song["external_urls"]["spotify"])
        skip()

    if inp == "reroll":  # REPRODUCE A MESMA PLAYLIST
        sp.start_playback(context_uri=sp.currently_playing()["context"]["uri"])
        time.sleep(0.7)
        now_playing()

    # - - - - STATS - - - - #
    if inp in ["top", "t"]:  # T - VER TOP
        try:
            inp = " "
            while inp not in ["/", ""]:
                printc("0 - last 4 weeks\n" "1 - last 6 months\n" "2 - total\n")
                inp = input("Choose (or '/' to cancel): ")
                if inp not in ["0", "1", "2"]:
                    inp = "/"

                else:
                    if not top_tracks["long_term"]:
                        printc("Loading data...")
                        load_top()
                    time_range = ranges[int(inp)]
                    ndatos = intput("\nChoose how many entries to see (1-50): ", 1, 50)

                    printc("\nMost played artists:")
                    i = 0
                    for artist in top_artists[time_range][:ndatos]:
                        i += 1
                        printc(str(i) + " - " + artist["name"])
                    input("Press Enter to continue..")
                    printc("\nMost played songs:")
                    i = 0
                    for track in top_tracks[time_range][:ndatos]:
                        i += 1
                        printc(str(i) + " - " + fullname(track))

                    printc("\n\n")

                    query = input("Save this data to a playlist? (y/n) ")
                    if query == "y":
                        play_id = create_top_playlist(ndatos, time_range)
                        query = input(
                            "Playlist succesfully created. Play now? (y/n) "
                        )
                        if query == "y":
                            play(sp.playlist(play_id))

            inp = "0"

        except Exception as e:
            report(e)

    # - - - - PLAYLIST CREATION - - - - #
    if inp == "make":
        p_name = ""
        while p_name == "":
            p_name = input("Playlist name: ")
        p_desc = "Created with troja."

        printc("\nWrite a list of new songs to add. Write / to finish.")
        seed_list = []
        song_list = []
        i = 0
        query = " "

        while query not in ["/", ""] and i < 5:
            try:
                query = input("\n - ").encode("utf-8").decode("utf-8")
            except Exception as E:
                report(E)
                continue
            if query not in ["/", ""]:
                song = sp.search(q=query, limit=5, type="track")["tracks"]["items"][0]
                song_list += [song["uri"]]

        printc("\nWrite a list of artists to add. Write / to finish. (up to 5 seeds)")
        art_list = []
        query = " "
        while query not in ["/", ""] and i < 5:
            query = input("\n - ")
            if query not in ["/", ""]:
                artist = sp.search(q=query, limit=6, type="artist")["artists"]["items"][
                    0
                ]
                art_list += [artist["uri"]]
                seed_list += [artist["name"]]
                i += 1

        if i < 5:
            printc(
                "\nWrite a list of genres to add. Write / to finish. Write ? to see a list of valid genres."
            )
        genre_list = []
        query = " "
        while query not in ["/", ""] and i < 5:
            query = input("\n - ")
            if query == "?":
                printc(sp.recommendation_genre_seeds()["genres"])
            elif query not in ["/", ""]:
                if query in sp.recommendation_genre_seeds()["genres"]:
                    genre_list += [query]
                    seed_list += [query]
                    i += 1
                else:
                    printc("Invalid genre.")

        limit = intput("How many new songs would you like to add? (0-100) ", 0, 100)
        play_id = sp.user_playlist_create(user_id, name=p_name, description=p_desc)[
            "uri"
        ]

        if len(song_list) > 0:
            sp.playlist_add_items(playlist_id=play_id, items=song_list)
            # en total podense meter 5 semillas. se entre os artistas e os generos hai menos de 5, completa collendo as
            # canciones que foron añadidas como semilla
        seed_songs = []
        j = 0
        while j < (5 - i) and j < len(song_list):
            seed_songs += [song_list[j]]
            seed_list += [sp.track(song_list[j])["name"]]
            j += 1

        if len(seed_list) == 0:
            printc("Cannot create an empty playlist!")

        else:
            expand_playlist(
                play_id,
                seed_artists=art_list,
                seed_tracks=seed_songs,
                seed_genres=genre_list,
                limit=limit,
            )

            printc("Seeds used: ")
            print(seed_list)

            p_desc += "includes "
            if i > 2:
                for seed in seed_list[0 : (i - 2)]:
                    p_desc += seed + ", "
            if i > 1:
                p_desc += seed_list[i - 2] + " e "
            p_desc += seed_list[i - 1] + "."
            sp.playlist_change_details(playlist_id=play_id, description=p_desc)
            inp = input("Playlist created. Play now? (y/n) ")
            if inp == "y":
                play(sp.playlist(play_id))

        # probablemente haba unha forma mellor de facer esto pero
        # dios non me puxo aquí para facer as cousas ben

    # EXPANDIR PLAYLIST CON RECOMENDACIÓNS
    if inp.startswith("expand "):
        printc("This feature has been deprecated due to changes to Spotify's API. You can read more here: "
               +"https://community.spotify.com/t5/Spotify-for-Developers/Changes-to-Web-API/td-p/6540414" +
               "\nSorry for the inconvenience :(", "light_red")
        continue
        query = inp.split("expand ")[1]
        p_name = difflib.get_close_matches(query, playlist_names, n=1, cutoff=0.6)
        if p_name:
            printc("Playlist found: " + p_name[0])
            play_id = playlists[playlist_names.index(p_name[0])]["uri"]
            printc(
                "\nWrite a list of artists to expand the playlist. Write / to finish. (up to 5 seeds)"
            )
            art_list = []
            seed_list = []
            query = " "
            i = 0
            while query not in ["/", ""] and i < 5:
                query = input("\n - ")
                if query not in ["/", ""]:
                    artist = sp.search(q=query, limit=5, type="artist")["artists"][
                        "items"
                    ][0]
                    art_list += [artist["uri"]]
                    seed_list += [artist["name"]]
                    i += 1

            if i < 5:
                printc(
                    "\nWrite a list of genres to expand the playlist. Write / to finish. (up to 5 seeds)"
                )

            genre_list = []
            query = " "
            while query not in ["/", ""] and i < 5:
                query = input("\n - ")
                if query == "?":
                    printc(sp.recommendation_genre_seeds()["genres"])
                elif query not in ["/", ""]:
                    if query in sp.recommendation_genre_seeds()["genres"]:
                        genre_list += [query]
                        seed_list += [query]
                        i += 1
                    else:
                        printc("Invalid genre.")

            limit = intput("How many new songs would you like to add? (0-100) ", 0, 100)
            expand_playlist(
                play_id, seed_artists=art_list, seed_genres=genre_list, limit=limit
            )
        else:
            printc("No matching playlist found.", "light_red")

    if inp == "expand":
        printc("This feature has been deprecated due to changes to Spotify's API. You can read more here: "
               +"https://community.spotify.com/t5/Spotify-for-Developers/Changes-to-Web-API/td-p/6540414" +
               "\nSorry for the inconvenience :(", "light_red")
        continue
        printc("Saved playlists: ")
        print(playlist_names)
        printc("Use expand [playlist] to expand a playlist.")

    # - - - - RECOMMENDATIONS - - - - #
    if inp in ["d", "discover"]:
    
        printc("This feature has been deprecated due to changes to Spotify's API. You can read more here: "
               +"https://community.spotify.com/t5/Spotify-for-Developers/Changes-to-Web-API/td-p/6540414" +
               "\nSorry for the inconvenience :(", "light_red")
        continue
        int_inp = intput(
            "0 - manual\n1 - based on top artists\n" + "<" + username + ">: ", 0, 1
        )
        art_list = []
        if int_inp == 0:
            printc("\nWrite a list of artists. Write / to finish. (up to 5 seeds)")
            query = " "
            i = 0
            while query not in ["/", ""] and i < 5:
                query = input("\n - ")
                if query not in ["/", ""]:
                    artist = sp.search(q=query, limit=6, type="artist")["artists"][
                        "items"
                    ][0]
                    art_list += [artist["uri"]]
                    i += 1
        if int_inp == 1:
            if not top_artists["short_term"]:
                load_top()
            for artist in top_artists["short_term"][:4]:
                art_list += [artist["uri"]]
        rec = sp.recommendations(seed_artists=art_list, limit=10)
        printc("Artists you may like: ")
        for track in rec["tracks"]:
            printc("\n- " + track["artists"][0]["name"])

    # - - - - DEBUG - - - - #
    if inp == "565678":
        p("hot to go!")

    if inp.startswith("what is love"):
        p("what is love - haddaway", silent=True)
        printc("baby don't hurt me")

    if inp == "ich bin wirklich krank":
        p("kugel im gesicht (9mm)", silent=True)
        printc("das ist einfach die Selbsterkenntnis.")

    if inp == "kuolonpyora":
        p("kuolonpyora")

    if inp == "troja":
        p("troja - in extremo")

    if inp == "mi cara cuando":
        p("bad romance - lady gaga")

    if inp == "ok":
        p("OK - rammstein")

    if inp == "bomba":
        printc("bomba cargada")

    if inp.startswith("nick "):
        username = inp.split("nick ")[1]

    if inp.startswith("color ") or inp.startswith("colors"):
        if inp.startswith("colors") or inp.split("color ")[1] not in colors:
            printc("valid colors: ")
            for color in colors:
                printc(" - " + colors[color] + color + colors["reset"])
        else:
            user_color = inp.split("color ")[1]

    if inp in ["viva españa", "arriba españa"]:
        if random.randint(0, 5) != 1:
            p("Himno de España - " "Legión Española")
        else:
            p("els segadors - banda republicana")

    if inp in ["root", "admin", "debug"]:
        input("enter root password: ")
        time.sleep(2)
        p("never gonna give you up", silent=True)


printc("shutting down ...", "blue")
