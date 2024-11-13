# bis Troja brennt!

import spotipy  # https://spotipy.readthedocs.io/en/2.24.0/
import time
import random
from fuzzywuzzy import process
from spotipy.oauth2 import SpotifyOAuth
import configparser

# <editor-fold desc="VARIABLES">
ranges = ['short_term', 'medium_term', 'long_term']
MAX_QUEUE = 5
playlists = []
playlist_names = []
top_artists = {'short_term': [], 'medium_term': [], 'long_term': []}
top_tracks = {'short_term': [], 'medium_term': [], 'long_term': []}
vocabulario = []

# Initialize parser
config = configparser.ConfigParser()
config.read('config.ini')

client_id = config.get('SPOTIPY', 'client_id')
client_secret = config.get('SPOTIPY', 'client_secret')
redirect_uri = config.get('SPOTIPY', 'redirect_uri')


# </editor-fold>

# <editor-fold desc="FUNCIÓNS">



def intput(prompt, min=0, max=9999):
    ans = None
    while ans is None:
        try:
            ans = int(input(prompt))
            if not min <= ans <= max:  # If outside the range, reset ans to None
                print('Introduza un número válido!!')
                ans = None
        except ValueError:
            print('Introduza un número válido!!')
            ans = None
    return ans


def fullname(track):
    return track['name'] + ' - ' + track['artists'][0]['name']


def now_playing():
    try:
        if sp.current_playback()['is_playing']:
            print('ahora sona:')
            print(fullname(sp.currently_playing()['item']))
    except Exception:
        print('non hai unha cola de reproducción activa. abre spotify nalgun dispositivo para comezar a reproducir')


def skip(silent=False):
    sp.next_track(device_id=None)
    if not silent:
        time.sleep(0.6)
        now_playing()


def play(playlist):
    if playlist['type'] == 'album':
        sp.shuffle(state=False)
        print('reproducindo álbum: ' + playlist['name'] + ' - ' + playlist['artists'][0]['name'])
    else:
        print('reproducindo álbum:' + playlist['name'] + ' (' + playlist['description'] + ') ')
        sp.shuffle(state=True)
    sp.start_playback(context_uri=playlist['uri'])
    time.sleep(0.7)
    now_playing()


def p(query, silent=False):  # plays a song w/o interrupting queue
    song = sp.search(q=query, limit=5, type='track')['tracks']['items'][0]
    sp.add_to_queue(song['external_urls']['spotify'])
    skip(silent)


def queue_uri(n):  # lee o uri dos n proximos da cola
    q_uri = []
    for k in range(n):
        q_uri += [sp.queue()['queue'][k]['uri']]
    return q_uri


def load_playlists():  # lee as playlists gardadas
    global playlist_names
    global playlists
    playlist_names = []
    playlists = sp.user_playlists(user_id)
    while playlists:
        for k, playlist in enumerate(playlists['items']):
            playlist_names += [playlist['name']]  # se tes dúas playlists co mesmo nome pos jodeste amigo
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

    playlists = sp.user_playlists(user_id)['items']


def create_top_playlist(n, time_range):
    tempos = {'short_term': ' do mes', 'medium_term': ' dos últimos 6 meses', 'long_term': ''}
    p_name = 'top ' + str(n) + tempos[time_range] + ' de ' + username
    print(p_name)
    p_desc = 'creado con troja'
    play_id = sp.user_playlist_create(user_id, name=p_name, description=p_desc)['uri']

    song_list = top_tracks[time_range][:n]
    k = 0
    for song in song_list:
        song_list[k] = song['uri']
        k += 1

    sp.playlist_add_items(playlist_id=play_id, items=song_list)

    return play_id


def expand_playlist(play_id, seed_artists=None, seed_tracks=None, seed_genres=None, limit=50):
    newsongs = \
        sp.recommendations(seed_artists=seed_artists, seed_tracks=seed_tracks, seed_genres=seed_genres, limit=limit)[
            'tracks']
    k = 0
    for song in newsongs:
        newsongs[k] = song['uri']
        k += 1

    sp.playlist_add_items(playlist_id=play_id, items=newsongs)


def init():
    print('\nbenvido, ' + username + '! (id: ' + user_id + ')')
    print('cargando playlists...')
    load_playlists()
    now_playing()
    print('escriba \'help\' para ver unha lista de comandos.')


def report(error):
    print('Produciuse un erro. (' + str(error) + ') ')


def load_top():
    global top_artists
    global top_tracks

    for time_range in ranges:
        top_artists[time_range] += sp.current_user_top_artists(limit=50, time_range=time_range)['items']
        top_tracks[time_range] += sp.current_user_top_tracks(limit=50, time_range=time_range)['items']


# <editor-fold desc="INIT">

scope = ["user-library-read", 'user-read-playback-state', 'user-modify-playback-state', 'playlist-modify-public',
         'playlist-modify-private',
         'user-top-read', 'playlist-read-private']
# https://developer.spotify.com/documentation/web-api/concepts/scopes

print('iniciando sesión...')
try:
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret,
                                  redirect_uri=redirect_uri))
except Exception as e:
    print('non se puido iniciar sesión !!')
    report(e)
    sp = None
    input('pulsa enter para que crashee inevitablemente o programa')

try:
    username = sp.me()['display_name']
    user_id = sp.me()['id']
    query = ''

    init()
except Exception as e:
    print('produciuse un erro inicializando!! a pesar de que se iniciou sesión ben!! o cal é estraño!!')
    report(e)
    input('pulsa enter para que crashee inevitablemente o programa')
    username = None
    user_id = None

inp = ''
warn_time = True

hangman = 0
errores = 6
intentos = []
h_palabra = []
h_guess = ''

# </editor-fold>

while inp != '/':
    inp = input('\n<' + username + '>: ').lower()

    # <editor-fold desc=" -- HELP --">
    if inp == 'help':
        print('/ - saír do programa\n'
               'q (+ cancion) - consulta cola actual, ou engade canción á cola \n'
               's, skip - salta canción actual\n'
               'p + cancion -  comeza a reproducir unha canción, sen interrumpir a cola\n'
               'play + playlist - comeza a reproducir unha playlist\n'
               'aplay + album - comeza a reproducir un álbum\n'
               'save + playlist - engade a canción actual a unha playlist \n'
               't, top - consulta cancións / artistas máis escoitados, e permite exportalos a unha playlist\n'
               'make - crea unha playlist, manualmente ou autocompletada co algoritmo de Spotify\n'
               'help+ - ver máis comandos')

    if inp == 'help+':
        print('reroll - randomiza a cola actual\n'
               'expand + playlist - expande unha playlist existente con recomendacións\n'
               'rec - comeza a reproducir unha recomendación aleatoria, baseándose na túa cola actual\n'
               'rec + artista - comeza a reproducir unha recomendación aleatoria dun artista \n'
               'd, discover - recomendache cancións, álbums ou artistas novos \n'
               '(inclúe un + tras o nome do artista para permitir artistas similares')

    # </editor-fold>

    # <editor-fold desc=" -- PLAYBACK -- ">
    if inp == 'q':  # Q - IMPRIMIR COLA
        now_playing()
        print('cola actual:')
        i = 0
        for track in sp.queue()['queue']:
            if i < MAX_QUEUE:
                print('\n - ' + fullname(track))
            i += 1

    if inp.startswith('q '):  # Q + CANCIÓN  -  ENGADIR CANCIÓN A COLA
        query = inp.split('q ')[1]

        try:
            song = sp.search(q=query, limit=1, type='track')['tracks']['items'][0]
            sp.add_to_queue(song['external_urls']['spotify'])

            print('engadido á cola:')
            print(fullname(song))
        except Exception as e:
            report(e)

    if inp == 'p':
        if sp.current_playback()['is_playing']:
            print('pausa!')
            sp.pause_playback()

        else:
            try:
                sp.start_playback()
                now_playing()

            except Exception as e:
                report(e)

    if inp.startswith('p '):  # P + CANCIÓN  -  ENGADIR CANCIÓN A COLA E REPRODUCILA
        query = inp.split('p ')[1]

        try:
            p(query)

        except Exception as e:
            report(e)

    if inp.startswith('play '):  # PLAY + PLAYLIST  -  REPRODUCIR PLAYLIST
        query = inp.split('play ')[1]

        try:
            p_name = process.extractOne(query, playlist_names)
            # print('prec: ' + str(p_name[1]))
            if p_name[1] > 86:  # se o que di o usuario se parece mas ou menos a algunha playlist gardada
                playlist = playlists[playlist_names.index(p_name[0])]
                play(playlist)
            else:
                inp = input('non se atopou ningunha playlist gardada con ese nome.\n'
                            '0 - cancelar\n'
                            '1 - buscar playlists en internet\n'
                            '2 - buscar álbums\n'
                            '<' + username + '>: ')
                if inp == '1':
                    playlist = sp.search(q=query, limit=1, type='playlist')['playlists']['items'][0]
                    play(playlist)
                if inp == '2':
                    playlist = sp.search(q=query, limit=1, type='album')['albums']['items'][0]
                    play(playlist)

        except Exception as e:
            report(e)

    if inp == 'play':
        print('As túas playlist gardadas: ')
        print(playlist_names)
        print('Podes usar play + un nome dunha playlist para reproducila.')

    if inp.startswith('save '):  # SAVE + PLAYLIST  -  GARDA A PLAYLIST
        query = inp.split('save ')[1]
        try:
            p_name = process.extractOne(query, playlist_names)
            if p_name[1] > 50:  # se o que di o usuario se parece mas ou menos a algunha playlist gardada
                playlist = playlists[playlist_names.index(p_name[0])]
                song = sp.currently_playing()['item']
                sp.playlist_add_items(playlist['uri'], [song['uri']])
                print('engadiuse \'' + fullname(song) + '\' á playlist \'' + p_name[0] + '\'')

            else:
                print('non se atopou a playlist!!!1!')
        except Exception as e:
            report(e)
    if inp.startswith('aplay '):  # APLAY + PLAYLIST  -  REPRODUCIR ÁLBUM
        query = inp.split('aplay ')[1]
        try:
            playlist = sp.search(q=query, limit=1, type='album')['albums']['items'][0]
            play(playlist)

        except Exception as e:
            report(e)

    if inp in ['skip', 's']:  # S -  SALTAR CANCIÓN
        try:
            skip()
        except Exception as e:
            report(e)

    if inp == 'rec':  # REC - REPRODUCIR RECOMENDACIÓN
        try:
            song = sp.recommendations(seed_tracks=(queue_uri(5)), limit=1)['tracks'][0]
            sp.add_to_queue(song['external_urls']['spotify'])
            skip()
        except Exception as e:
            report(e)
            report(e)

    if inp.startswith('rec '):
        inp = inp.split('rec ')[1]
        artist = sp.search(q=inp, limit=5, type='artist')['artists']['items'][0]
        song = sp.recommendations(seed_artists=[artist['uri']], limit=1)['tracks'][0]
        if not inp.endswith('+') and warn_time:  # este aviso solo salta unha vez
            print('dependendo do artista, '
                   'isto pode tardar un cacho pola forma na que funciona o algoritmo de recomendacions de spotify :(')
            warn_time = False
        while (song['artists'][0]['name'] != artist['name']) and not inp.endswith('+'):
            song = sp.recommendations(seed_artists=[artist['uri']], limit=1)['tracks'][0]

        sp.add_to_queue(song['external_urls']['spotify'])
        skip()

    if inp == 'reroll':  # REPRODUCE A MESMA PLAYLIST
        sp.start_playback(context_uri=sp.currently_playing()['context']['uri'])
        time.sleep(0.7)
        now_playing()

    # </editor-fold>

    # <editor-fold desc=" -- STATS -- ">
    if inp in ['top', 't']:  # T - VER TOP
        try:
            inp = ' '
            while inp not in ['/', '']:
                print('0 - últimas 4 semanas\n'
                       '1 - últimos 6 meses\n'
                       '2 - total\n')
                inp = input('Escolla (ou \'/\' para saír): ')
                if inp not in ['0', '1', '2']:
                    inp = '/'

                else:
                    if not top_tracks['long_term']:
                        print('cargando datos...')
                        load_top()
                    time_range = ranges[int(inp)]
                    ndatos = intput('\nNúmero de datos que imprimir (1-50): ', 1, 50)

                    print('\nArtistas máis escoitados:')
                    i = 0
                    for artist in top_artists[time_range][:ndatos]:
                        i += 1
                        print(str(i) + ' - ' + artist['name'])
                    input('Prema enter para continuar...')
                    print('\nCancións máis escoitadas:')
                    i = 0
                    for track in top_tracks[time_range][:ndatos]:
                        i += 1
                        print(str(i) + ' - ' + track['name'])

                    print('\n\n')

                    query = input('Gardar estos datos nunha playlist? (y/n) ')
                    if query == 'y':
                        play_id = create_top_playlist(ndatos, time_range)
                        query = input('playlist creada. completar con recomendacións? (y/n) ')
                        if query == 'y':
                            limit = intput('cantas cancións engadir? (1-100) ', 1, 100)
                            if 0 < limit < 101:
                                art_list = []
                                for artist in top_artists[time_range][:5]:
                                    art_list += [artist['uri']]
                                expand_playlist(play_id, art_list, limit=limit)
                                print('playlist expandida con ' + str(limit) + ' novas cancións.')

            inp = '0'

        except Exception as e:
            report(e)
    # </editor-fold>

    # <editor-fold desc="-- MAKE / EDIT PLAYLIST --">
    if inp == 'make':
        p_name = ''
        while p_name == '':
            p_name = input('Nome da playlist: ')
        p_desc = 'creado con troja'

        print('Escribe unha lista de cancións que engadir. Escribe / para finalizar.')
        seed_list = []
        song_list = []
        i = 0
        query = ' '

        while query not in ['/', ''] and i < 5:
            query = input('\n - ')
            if query not in ['/', '']:
                song = sp.search(q=query, limit=5, type='track')['tracks']['items'][0]
                song_list += [song['uri']]

        print('\nEscribe unha lista de artistas que sirvan para completar a playlist. Escribe / para finalizar.  (en '
               'total, pódense empregar un máx. de 5 semillas)')
        art_list = []
        query = ' '
        while query not in ['/', ''] and i < 5:
            query = input('\n - ')
            if query not in ['/', '']:
                artist = sp.search(q=query, limit=6, type='artist')['artists']['items'][0]
                art_list += [artist['uri']]
                seed_list += [artist['name']]
                i += 1

        if i < 5:
            print('\nEscribe unha lista de xéneros que sirvan para completar a playlist. Escribe / para finalizar. '
                   'Escribe ? para ver unha lista de xéneros válidos.')
        genre_list = []
        query = ' '
        while query not in ['/', ''] and i < 5:
            query = input('\n - ')
            if query == '?':
                print(sp.recommendation_genre_seeds()['genres'])
            elif query not in ['/', '']:
                if query in sp.recommendation_genre_seeds()['genres']:
                    genre_list += [query]
                    seed_list += [query]
                    i += 1
                else:
                    print('Xénero inválido.')

        limit = intput('Cantas cancións novas engadir? (0-100)', 0, 100)
        play_id = sp.user_playlist_create(user_id, name=p_name, description=p_desc)['uri']

        if len(song_list) > 0:
            sp.playlist_add_items(playlist_id=play_id, items=song_list)
            # en total podense meter 5 semillas. se entre os artistas e os generos hai menos de 5, completa collendo as
            # canciones que foron añadidas como semilla
        seed_songs = []
        j = 0
        while j < (5 - i) and j < len(song_list):
            seed_songs += [song_list[j]]
            seed_list += [sp.track(song_list[j])['name']]
            j += 1

        if len(seed_list) == 0:
            print('non seleccionaches nada. que ques facer unha playlist vacia? fache falta un programa pa eso? '
                   'madura.')
        else:
            expand_playlist(play_id, seed_artists=art_list, seed_tracks=seed_songs, seed_genres=genre_list, limit=limit)

            print('Semillas utilizadas: ')
            print(seed_list)

            p_desc += '. inclúe '
            if i > 2:
                for seed in seed_list[0:(i - 2)]:
                    p_desc += (seed + ', ')
            if i > 1:
                p_desc += (seed_list[i - 2] + ' e ')
            p_desc += seed_list[i - 1] + '.'
            sp.playlist_change_details(playlist_id=play_id, description=p_desc)
            inp = input('Playlist creada. Reproducir ahora? (y/n) ')
            if inp == 'y':
                play(sp.playlist(play_id))

        # probablemente haba unha forma mellor de facer esto pero
        # dios non me puxo aquí para facer as cousas ben

    # EXPANDIR PLAYLIST CON RECOMENDACIÓNS
    if inp.startswith('expand '):
        query = inp.split('expand ')[1]
        p_name = process.extractOne(query, playlist_names)
        play_id = playlists[playlist_names.index(p_name[0])]['uri']

        print('\nEscribe unha lista de artistas que sirvan para completar a playlist. Escribe / para finalizar.  (en '
               'total, pódense empregar un máx. de 5 semillas)')
        art_list = []
        seed_list = []
        query = ' '
        i = 0
        while query not in ['/', ''] and i < 5:
            query = input('\n - ')
            if query not in ['/', '']:
                artist = sp.search(q=query, limit=5, type='artist')['artists']['items'][0]
                art_list += [artist['uri']]
                seed_list += [artist['name']]
                i += 1

        if i < 5:
            print('\nEscribe unha lista de xéneros que sirvan para completar a playlist. Escribe / para finalizar. '
                   'Escribe ? para ver unha lista de xéneros válidos.')
        genre_list = []
        query = ' '
        while query not in ['/', ''] and i < 5:
            query = input('\n - ')
            if query == '?':
                print(sp.recommendation_genre_seeds()['genres'])
            elif query not in ['/', '']:
                if query in sp.recommendation_genre_seeds()['genres']:
                    genre_list += [query]
                    seed_list += [query]
                    i += 1
                else:
                    print('Xénero inválido.')

        limit = intput('Cantas cancións novas engadir? (0-100)', 0, 100)
        expand_playlist(play_id, seed_artists=art_list, seed_genres=genre_list, limit=limit)
        print('Engadíronse ' + str(limit) + ' cancións.')

    # </editor-fold>

    if inp in ['d', 'discover']:
        inp = intput(
            '0 - introduce unha lista de artistas para recibir recomendacións doutros artistas similares \n'
            '1 - ver recomendacións baseándose nos teus artistas favoritos (do último mes)\n'
            '<' + username + '>: ', 0, 1)
        art_list = []
        if inp == 0:
            print(
                '\nEscribe unha lista de artistas. Escribe / para finalizar.  (en '
                'total, pódense empregar un máx. de 5 semillas)')
            query = ' '
            i = 0
            while query not in ['/', ''] and i < 5:
                query = input('\n - ')
                if query not in ['/', '']:
                    artist = sp.search(q=query, limit=6, type='artist')['artists']['items'][0]
                    art_list += [artist['uri']]
                    i += 1
        if inp == 1:
            if not top_artists['short_term']:
                load_top()
            for artist in top_artists['short_term'][:4]:
                art_list += [artist['uri']]
        rec = sp.recommendations(seed_artists=art_list, limit=10)
        print('pódenche gustar: ')
        for track in rec['tracks']:
            print('\n- ' + track['artists'][0]['name'])
        continue

    # <editor-fold desc="DEBUG">
    if inp == '565678':
        p('hot to go!')

    if inp.startswith('what is love'):
        p('what is love - haddaway', silent=True)
        print('baby don\'t hurt me')

    if inp == 'ich bin wirklich krank':
        p('kugel im gesicht (9mm)', silent=True)
        print('das ist einfach die Selbsterkenntnis.')

    if inp == 'kuolonpyora':
        p('kuolonpyora')

    if inp == 'troja':
        p('troja - in extremo')

    if inp == 'mi cara cuando':
        p('bad romance - lady gaga')

    if inp == 'ok':
        p('OK - rammstein')

    if inp == 'bomba':
        print('bomba cargada')

    if inp.startswith('/nick '):
        username = inp.split('/nick ')[1]

    if inp in ['viva españa', 'arriba españa']:
        if random.randint(0, 5) != 1:
            p('Himno de España - '
              'Legión Española')
        else:
            p('els segadors - banda republicana', silent=True)
            print('ahora sona: Himno de España - '
                   'Legión Española')

    if inp in ['root', 'admin', 'debug']:
        input('enter root password: ')
        time.sleep(2)
        p('never gonna give you up', silent=True)

    # </editor-fold>

print('cerrando o programa ...')
