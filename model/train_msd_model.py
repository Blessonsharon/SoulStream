"""
SoulStream MSD Intelligence Engine — Hybrid KNN Trainer
========================================================
Trains a Nearest-Neighbours model on the Million Song Dataset using:
  - Numeric audio features : tempo, loudness, mode
  - Text genre/vibe tags   : TF-IDF over Last.fm artist terms

The model becomes an expert in mapping emotions → genre clusters → songs.
iTunes is used only to deliver the actual playable track (audio preview + art).
"""
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import hstack, csr_matrix

CSV_PATH   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "local_10k_songs.csv"))
MODEL_PATH = os.path.join(os.path.dirname(__file__), "msd_knn_model.pkl")

# ── Emotion Centroids ──────────────────────────────────────────────
# Numeric: [tempo (BPM), loudness (dB), mode (0=minor,1=major)]
# Genre  : descriptive string of genre/tag keywords the model learns to understand
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

AUDIO_COLS = ["tempo", "loudness", "mode"]


def train():
    print("=" * 60)
    print("SoulStream — Hybrid MSD Intelligence Engine Training")
    print("=" * 60)

    df = pd.read_csv(CSV_PATH).dropna(subset=AUDIO_COLS + ["vibes"])
    df = df[df["tempo"] > 0]           # Drop silent/corrupt entries
    df["vibes"] = df["vibes"].fillna("").astype(str)
    df = df.reset_index(drop=True)
    print(f"Loaded {len(df)} valid tracks from MSD dataset")

    # ── 1. Scale numeric audio features ──
    audio_data = df[AUDIO_COLS].values.astype(float)
    scaler = StandardScaler()
    audio_scaled = csr_matrix(scaler.fit_transform(audio_data))

    # ── 2. TF-IDF on genre/artist tags — model learns genre semantics ──
    tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    genre_matrix = tfidf.fit_transform(df["vibes"])
    print(f"TF-IDF genre vocabulary: {len(tfidf.vocabulary_)} unique genre terms learned")

    # ── 3. Combine both feature spaces into one hybrid matrix ──
    # Weight audio higher (x2) so BPM/key guides the recommendation
    combined = hstack([audio_scaled * 2.0, genre_matrix])
    print(f"Hybrid feature matrix shape: {combined.shape}")

    # ── 4. Train KNN on hybrid space ──
    knn = NearestNeighbors(n_neighbors=50, metric='cosine', algorithm='brute')
    knn.fit(combined)
    print("KNN model fitted on hybrid feature space")

    # ── 5. Validate: show which songs each emotion maps to ──
    print("\nSample songs per emotion (from 10k dataset):")
    for emotion, centroid in EMOTION_CENTROIDS.items():
        audio_vec = scaler.transform([centroid["audio"]]) * 2.0
        genre_vec = tfidf.transform([centroid["genre"]])
        query_vec = hstack([csr_matrix(audio_vec), genre_vec])
        distances, indices = knn.kneighbors(query_vec, n_neighbors=5)
        top = df.iloc[indices[0]][['name', 'artist']].values[0]
        print(f"  {emotion:20s} -> '{top[0]}' by {top[1]}")

    # ── 6. Save full model bundle ──
    bundle = {
        "knn": knn,
        "scaler": scaler,
        "tfidf": tfidf,
        "df": df
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)

    print(f"\nModel bundle saved to: {MODEL_PATH}")
    print("=" * 60)
    print("Ready! Now recommender.py will use this to pick songs,")
    print("then fetch audio previews from iTunes automatically.")
    print("=" * 60)


if __name__ == "__main__":
    train()
