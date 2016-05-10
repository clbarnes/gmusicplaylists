from gmusicapi import Mobileclient
import warnings
import base64


SCORE_THRESHOLD = 0


def sanitise_query(query):
    query = query.lower()
    query = query.replace(' x ', ' ')
    query = query.replace(' & ', ' ')
    query = query.replace(' (feat. ', ' ')
    query = query.replace(') ', ' ')
    query = query.replace(' featuring ', ' ')
    return query


def is_tribute(track, query):
    query = query.lower()
    s = ' '.join([track['title'].lower(), track['artist'].lower(), track['album'].lower()])
    if any([buzzword in s for buzzword in ['tribute to', 'originally performed by', 'in the style', 'inspir', 'karaoke']]):
        if not any([buzzword in query for buzzword in ['tribute', 'originally', 'in the style', 'inspir', 'karaoke']]):
            return True

    return False


def decrypt(s):
    return base64.b64decode(s).decode()


class GMusicAPI():
    def __init__(self, username=None, encrypted_pass=None):
        self._api = Mobileclient()
        self.logged_in = False
        if username and encrypted_pass:
            self.login(username, encrypted_pass)

    def login(self, username, encrypted_pass):
        self.logged_in = self._api.login(username, decrypt(encrypted_pass), Mobileclient.FROM_MAC_ADDRESS)

    def logout(self):
        self._api.logout()
        self.logged_in = False

    def clear_playlist(self, playlist_name):
        playlists = self._api.get_all_user_playlist_contents()
        playlist = [playlist for playlist in playlists if playlist['name'] == playlist_name][0]
        entry_ids = [entry['id'] for entry in playlist['tracks']]
        removed = self._api.remove_entries_from_playlist(entry_ids)
        return len(removed)

    def search(self, *args):
        """
        Returns the best-fitting track dict for the given information.
        :param args: Strings which can be artist, song title, album etc.
        :return:
        """
        query = sanitise_query(' '.join(args))

        result = self._api.search(query)

        song_results = result['song_hits']
        if not song_results:
            warnings.warn('Warning: query {} returned no song hits.'.format(query))
            return None

        tracks = [song_result['track'] for song_result in song_results[:5]]

        for track in tracks:
            if not is_tribute(track, query):
                return track

        warnings.warn('Warning: query {} returned no non-tribute song hits.'.format(query))
        return None

    def get_playlist_id(self, playlist_name):
        for playlist in self._api.get_all_playlists():
            if playlist['name'] == playlist_name:
                return playlist['id']
        raise ValueError("Playlist '{}' not found".format(playlist_name))

    def add_songs(self, playlist_name, tracks):
        playlist_id = self.get_playlist_id(playlist_name)
        track_ids = [track['nid'] for track in tracks if track]
        self._api.add_songs_to_playlist(playlist_id, track_ids)