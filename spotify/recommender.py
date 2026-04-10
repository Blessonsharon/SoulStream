"""
SoulStream Recommender Engine
==============================
Flow:
  1. MSD KNN model selects the most sonically/genre-relevant songs from 10k dataset
     based on the detected emotion (learned from tempo + loudness + mode + genre tags)
  2. For each selected song, queries iTunes Open API to get:
       - Official album art
       - 30-second audio preview
       - Full Apple Music link
  3. Falls back to pure iTunes fuzzy search if KNN model not found
"""
import os
import random
import pickle
import requests
import urllib.parse
import numpy as np
from scipy.sparse import hstack, csr_matrix

from .artist_discovery import get_similar_artists

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "msd_knn_model.pkl")

# Emotion → Audio centroid + genre description (must match train_msd_model.py exactly)
EMOTION_CENTROIDS = {
    "happy":          {"audio": [120, -5,   1], "genre": "pop upbeat dance feel-good indie fun"},
    "sad":            {"audio": [ 70, -15,  0], "genre": "acoustic folk melancholy blues soul quiet"},
    "angry":          {"audio": [155, -4,   0], "genre": "metal punk hardcore alternative heavy noise"},
    "neutral":        {"audio": [ 95, -10,  1], "genre": "ambient chill lofi indie pop soft background"},
    "party":          {"audio": [128, -4,   1], "genre": "edm dance club house techno electronic pop party"},
    "lust":           {"audio": [ 88, -9,   0], "genre": "rnb slow jam neo soul sensual smooth"},
    "hangover":       {"audio": [ 72, -14,  1], "genre": "acoustic singer-songwriter chill folk soft quiet"},
    "breakup":        {"audio": [ 68, -13,  0], "genre": "sad ballad heartbreak acoustic soul indie folk"},
    "depression":     {"audio": [ 58, -17,  0], "genre": "sad melancholy dark slow ambient minimal drone"},
    "lonely":         {"audio": [ 74, -14,  0], "genre": "acoustic folk indie sad quiet reflective"},
    "stressed":       {"audio": [130, -7,   0], "genre": "alternative rock indie noise heavy intense"},
    "anxiety":        {"audio": [125, -8,   0], "genre": "electronic alternative dark moody tense"},
    "adrenaline rush":{"audio": [165, -3,   1], "genre": "metal hardcore electronic heavy hype aggressive bass"},
    "gym":            {"audio": [145, -3,   1], "genre": "hip hop trap electronic workout bass heavy hype"},
    "athletic":       {"audio": [135, -5,   1], "genre": "rock pop hip hop energetic upbeat motivational"},
    "love":           {"audio": [ 90, -8,   1], "genre": "pop soul rnb romantic ballad warm acoustic"},
    "aesthetic":      {"audio": [ 85, -12,  1], "genre": "indie chillwave dream-pop ambient lo-fi shoegaze"},
}

# Fallback generic iTunes search terms
EMOTION_SEARCH = {
    "happy": "upbeat happy pop", "sad": "sad acoustic melancholy", "angry": "heavy metal punk",
    "neutral": "chill lofi ambient", "party": "dance club electronic", "lust": "rnb slow jam sensual",
    "hangover": "chill acoustic soft", "breakup": "heartbreak ballad sad", "depression": "dark slow minimal",
    "lonely": "lonely acoustic folk", "stressed": "tense alternative rock", "anxiety": "moody electronic dark",
    "adrenaline rush": "hype heavy bass metal", "gym": "workout trap hip hop hype", "athletic": "motivational rock energetic",
    "love": "romantic soul pop", "aesthetic": "dream pop lo-fi indie chill"
}

_knn_bundle = None


def _load_model():
    global _knn_bundle
    if _knn_bundle is None and os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            _knn_bundle = pickle.load(f)
    return _knn_bundle


def _query_itunes(song_name: str, artist_name: str, country: str = "us") -> dict | None:
    """Fetch a specific song from iTunes by name + artist."""
    q = urllib.parse.quote_plus(f"{song_name} {artist_name}")
    try:
        r = requests.get(f"https://itunes.apple.com/search?term={q}&entity=song&limit=1&country={country}", timeout=4)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                t = results[0]
                return {
                    "name": t.get("trackName", song_name),
                    "artist": t.get("artistName", artist_name),
                    "album": t.get("collectionName", "Unknown Album"),
                    "url": t.get("trackViewUrl", "#"),
                    "id": str(t.get("trackId", "")),
                    "image": t.get("artworkUrl100", "").replace("100x100bb", "300x300bb"),
                    "preview": t.get("previewUrl", "")
                }
    except Exception:
        pass
    return None


def _query_itunes_broad(query: str, limit: int = 30, country: str = "us") -> list:
    """Broad iTunes search — used as fallback."""
    results = []
    try:
        q = urllib.parse.quote_plus(query)
        r = requests.get(f"https://itunes.apple.com/search?term={q}&entity=song&limit={limit}&country={country}", timeout=5)
        if r.status_code == 200:
            for t in r.json().get("results", []):
                results.append({
                    "name": t.get("trackName", "Unknown"),
                    "artist": t.get("artistName", "Unknown"),
                    "album": t.get("collectionName", "Unknown"),
                    "url": t.get("trackViewUrl", "#"),
                    "id": str(t.get("trackId", "")),
                    "image": t.get("artworkUrl100", "").replace("100x100bb", "300x300bb"),
                    "preview": t.get("previewUrl", "")
                })
    except Exception:
        pass
    return results


def get_recommendations(emotion: str, keywords: list = None, favorite_artists: list = None,
                         mentioned_artists: list = None, genre: str = None,
                         context_text: str = "", limit: int = 10,
                         itunes_country: str = "us") -> dict:

    bundle = _load_model()

    # ── PATH 1: KNN Model is available ──────────────────────────────────────
    if bundle:
        centroid = EMOTION_CENTROIDS.get(emotion, EMOTION_CENTROIDS["neutral"])
        scaler = bundle["scaler"]
        tfidf  = bundle["tfidf"]
        knn    = bundle["knn"]
        df     = bundle["df"]

        audio_vec  = csr_matrix(scaler.transform([centroid["audio"]])) * 2.0
        genre_text = centroid["genre"]
        if keywords:
            genre_text += " " + " ".join(keywords)
        genre_vec  = tfidf.transform([genre_text])
        query_vec  = hstack([audio_vec, genre_vec])

        distances, indices = knn.kneighbors(query_vec, n_neighbors=min(50, len(df)))
        candidates = df.iloc[indices[0]].copy()

        seed_artists = mentioned_artists or favorite_artists or []
        if seed_artists:
            def artist_boost(row):
                for a in seed_artists:
                    if a.lower() in str(row["artist"]).lower():
                        return 2
                return 1
            candidates["boost"] = candidates.apply(artist_boost, axis=1)
            candidates = candidates.sort_values("boost", ascending=False)

        pool = candidates.head(30)
        picks = pool.sample(n=min(limit, len(pool)))

        songs = []
        for _, row in picks.iterrows():
            result = _query_itunes(row["name"], row["artist"], country=itunes_country)
            if result:
                songs.append(result)

        if songs:
            return {"songs": songs, "source": "msd_knn", "query": emotion}

    # ── PATH 2: Fallback to iTunes fuzzy + artist discovery ─────────────────
    seed_artists = mentioned_artists or favorite_artists or []
    expanded_artists = list(seed_artists)
    for a in seed_artists:
        expanded_artists.extend(get_similar_artists(a, limit=2))
    random.shuffle(expanded_artists)

    base_query = EMOTION_SEARCH.get(emotion, emotion)
    if expanded_artists:
        base_query = f"{expanded_artists[0]} {base_query}"

    results = _query_itunes_broad(base_query, limit=limit * 3, country=itunes_country)
    random.shuffle(results)
    return {"songs": results[:limit], "source": "itunes_fallback", "query": base_query}
