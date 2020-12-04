# Welcome to flowsy
> A simple way to get recommendations.


```python
%load_ext autoreload
%autoreload 2
```

    The autoreload extension is already loaded. To reload it, use:
      %reload_ext autoreload
    

This file will become your README and also the index of your documentation.

## Install

`pip install flowsy`

## How to use

If you want to say hello to someone you can use this method

```python
say_hello("Daniel")
```




    'Hello Daniel!'



```python
path_models = Path("D:/schule/diplomarbeit/models")
mpd_csv_file = r"D:\schule\diplomarbeit\converted_csv\mpd_slice_0-9999.csv"

save = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath   
playlist_learner = load_learner(path_models/'playlists_tracks_br_model_v1.pkl')
artist_learner = load_learner(path_models/'playlists_artists_br_model_v1.pkl')
pathlib.PosixPath = save

playlists = pd.read_csv(mpd_csv_file, delimiter=',', encoding='utf-8', header=None, low_memory=False,
                       names=['pid','track_uri','rating','playlist_name','track_name','artist_uri','artist_name'], skiprows=1)
```

```python
rec = Recommender(p_learn=playlist_learner, a_learn=artist_learner, playlists=playlists)
```

```python
rankings = rec.recommend(255)
rankings
```
