from configparser import ConfigParser
from .api_tools import GMusicAPI
from .get_charts import get_hot_100


get_tracks = {
    'hot100': get_hot_100,
    # 'top40': get_top_40
}

cfg = ConfigParser()

cfg.read(['credentials.ini'])

username = cfg.get('credentials', 'username')
password_enc = cfg.get('credentials', 'password')

api = GMusicAPI()
api.login(username, password_enc)

for playlist, chart_getter in get_tracks.items():
    playlist_name = cfg.get(playlist, 'playlist_name')
    api.clear_playlist(playlist_name)
    tracks_info = get_tracks[playlist]()
    tracks = [api.search(*track_info) for track_info in tracks_info]
    api.add_songs(playlist_name, tracks)

api.logout()

print('Done')