# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['Recommender', 'Ranking', 'sigmoid']

# Cell
from fastai.collab import *
from fastai.tabular.all import *

# Cell
class Recommender:
    def __init__(self, p_learn, a_learn, playlists):
        self.p_learn = p_learn
        self.p_dls = p_learn.dls
        self.a_learn = a_learn
        self.a_dls = a_learn.dls
        self.playlists = playlists

    def recommend(self, pid, sim_artists=4, sim_playlists=100, artist_variety=2, inc_artist=True, inc_similar=True):
        artists = self.__get_artists(pid) #dict
        similar_artists = self.__get_similar_artists(artists, sim_artists) #list
        pids = self.__get_similar_playlists(pid, sim_playlists)
        rankings = self.__get_rankings(pids)
        if(inc_artist):
            self.__inc_ranking_artist(rankings, artists)
        if(inc_similar):
            self.__inc_ranking_similar_artist(rankings, similar_artists)
        filtered_rankings = self.__remove_duplicates(rankings, pid)
        filtered_rankings.sort(key=lambda x: x.rating, reverse=True)
        top_track_uris = self.__limit_artists(filtered_rankings, artist_variety)
        return top_track_uris

    def __get_artists(self, pid):
        artists = {}
        artist_uris = list(self.playlists.loc[self.playlists['pid'] == pid]['artist_uri'])
        for artist_uri in artist_uris:
            artists[artist_uri] = artist_uris.count(artist_uri)
        return artists

    def __get_similar_artists(self, artists, sim_artists):
        similar_artists = []
        artist_factors = self.a_learn.model.i_weight.weight
        for artist_uri in artists:
            idx = self.a_dls.classes['artist_uri'].o2i[artist_uri]
            distances = nn.CosineSimilarity(dim=1)(artist_factors, artist_factors[idx][None])
            idxs = distances.argsort(descending=True)[1:sim_artists]
            similar_artist_uris = list(self.a_dls.classes['artist_uri'][idxs])
            similar_artists.extend(similar_artist_uris)

        similar_artists_filtered = [similar_artist for similar_artist in similar_artists if similar_artist not in artists]
        return similar_artists_filtered

    def __get_similar_playlists(self, pid, sim_playlists):
        playlist_factors = self.p_learn.model.u_weight.weight
        idx = self.p_dls.classes['pid'].o2i[pid]
        distances = nn.CosineSimilarity(dim=1)(playlist_factors, playlist_factors[idx][None])
        idxs = distances.argsort(descending=True)[1:sim_playlists]
        return list(self.p_dls.classes['pid'][idxs])

    def __get_rankings(self, pids):
        rankings = []
        count = 1
        for p in pids:
            track_uris = list(self.playlists.loc[self.playlists['pid'] == p]['track_uri'])
            artist_uris = list(self.playlists.loc[self.playlists['pid'] == p]['artist_uri'])
            for track_uri, artist_uri in zip(track_uris, artist_uris):
                ranking = Ranking(track_uri, artist_uri, count, p)
                rankings.append(ranking)
            if(count > 0):
                count -= 0.05
        return rankings

    def __inc_ranking_artist(self, rankings, artists):
        for ranking in rankings:
            if ranking.artist_uri in artists:
                ranking.rating = ranking.rating + sigmoid(artists[ranking.artist_uri])

    def __inc_ranking_similar_artist(self, rankings, similar_artists):
        for ranking in rankings:
            if ranking.artist_uri in similar_artists:
                ranking.rating = ranking.rating + 1

    def __remove_duplicates(self, rankings, pid):
        unique_rankings = list(set(rankings))

        tracks_of_playlist = list(self.playlists.loc[self.playlists['pid'] == pid]['track_uri'])
        return list([unique_ranking for unique_ranking in unique_rankings if not unique_ranking.track_uri in tracks_of_playlist])

    def __limit_artists(self, rankings, artist_variety):
        top_track_uris = []
        final_rankings = []
        for ranking in rankings:
            count = sum(final_ranking.artist_uri == ranking.artist_uri for final_ranking in final_rankings)
            if(count < artist_variety):
                final_rankings.append(ranking)
        return list([ranking.track_uri for ranking in final_rankings])

# Cell
class Ranking:
    def __init__(self, track_uri, artist_uri, rating, pid):
        self.track_uri = track_uri
        self.artist_uri = artist_uri
        self.rating = rating
        self.pid = pid

    def __eq__(self, other):
        return self.track_uri == other.track_uri

    def __hash__(self):
        return hash(('track_uri', self.track_uri))

# Cell
def sigmoid(x):
    return 2 * (1 / (1 + math.exp(-x)) - 0.5)