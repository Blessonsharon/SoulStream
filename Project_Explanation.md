# SoulStream — Project Explanation

## Overview

SoulStream is a fully offline, emotion-driven music recommendation system. It detects a user's current mood through three different computer-vision and NLP pipelines — all running locally without any cloud AI API keys — and then recommends music by querying the free Apple iTunes REST API, which provides album art, 30-second previews, and full Apple Music links at no cost.

This document explains the technical design of every major component.

---

## Core Components

### 1. Text Emotion Engine (`model/predict.py`)

The text pipeline runs in two tiers, in order of priority:

**Tier 1 — Zero-Shot Dictionary (Hyper-Granular)**

Before any ML inference, the raw input text is scanned against a curated dictionary of regex patterns mapped to 12 complex lifestyle emotions (`party`, `lust`, `hangover`, `breakup`, `depression`, `lonely`, `stressed`, `anxiety`, `adrenaline rush`, `gym`, `athletic`, `love`). If any pattern matches, the emotion is returned immediately with 99% confidence, bypassing the ML model entirely. This ensures emotionally specific inputs (e.g., "I'm going to the gym") are never mis-classified as generic "happy" or "sad".

**Tier 2 — Trained ML Classifier (Generic Sentiment)**

If no explicit keyword matches, a pre-trained **TF-IDF + SVM pipeline** (`model/local_text_model.pkl`) is loaded. It was trained on the HuggingFace emotions dataset (`data/huggingface_emotions.csv`, ≈400k samples) and classifies into four base states: `happy`, `sad`, `angry`, `neutral`. Probability scores for all classes are returned to the UI for confidence visualization.

Artist names mentioned in text are also extracted via a simple regex dictionary lookup (`KNOWN_ARTISTS`) and passed to the recommender as boosting signals.

---

### 2. Facial Emotion Detection (`model/vision.py`)

Uses **OpenCV Haar Cascades** — a classical, purely local computer vision technique. No neural network DLLs (TensorFlow/PyTorch) are involved. The algorithm:

1. Detects faces using `haarcascade_frontalface_default.xml`
2. Within the face ROI, detects smiles using `haarcascade_smile.xml`
3. If a smile is found → `happy`
4. Otherwise, measures average pixel brightness of the face ROI:
   - Brightness < 90 → `sad` (dark, moody lighting)
   - Brightness > 180 → `angry` (overexposed, intense)
   - Otherwise → `neutral`

This deliberately avoids heavy ONNX/TensorFlow FER models to ensure the app runs without GPU or large DLL dependencies.

---

### 3. Aesthetic Story Vibe (`model/story_vibe.py`)

For photos where the subject is a scene rather than a face (Instagram stories, landscapes, social media posts), the image is analyzed mathematically using **HSV color-space decomposition**:

| Condition | Detected Vibe | Music Genre |
|---|---|---|
| `avg_val < 70` | Midnight Dark | LoFi, sleep, moody |
| `avg_val > 180` | Sunny Bright | Summer pop, beach |
| High saturation + Red/Orange hue | Golden Hour | Warm acoustic, indie |
| High saturation + Purple/Blue hue | Neon/Cyberpunk | Synthwave, late night |
| High saturation + Green hue | Nature/Forest | Folk, adventure |
| Default | Casual Chill | Coffeehouse, acoustic |

The output emotion is always `aesthetic` with a genre keyword string that feeds directly into the iTunes search.

---

### 4. Landmark Intelligence (`model/landmark_detector.py`)

To identify famous world locations from photos, SoulStream uses **HuggingFace CLIP** (`openai/clip-vit-base-patch32`) via the free public HuggingFace Inference API. CLIP performs zero-shot image classification: the image is compared against 60+ landmark label strings (e.g., "Eiffel Tower", "Taj Mahal") and the highest-scoring match is returned.

Each landmark in `LANDMARK_DB` is pre-mapped to:
- Country & language
- Culturally relevant music genre tags
- iTunes country storefront code

If the confidence score exceeds a minimum threshold (~5%), the landmark is accepted and music is routed to that country's iTunes storefront automatically.

---

### 5. Location Intelligence (`model/location_detector.py`)

When a photo is uploaded, its EXIF metadata is read using Pillow. If GPS coordinates are present (latitude/longitude), they are reverse-geocoded to a city and country using the free **Nominatim / OpenStreetMap API**. A Wikipedia thumbnail of the detected city is also fetched. The detected country overrides the user's manual region selection when routing to iTunes storefronts.

---

### 6. Music Recommendation Engine (`spotify/recommender.py`)

The recommender operates in two paths:

**Path 1 — MSD KNN Model (Primary)**

A pre-trained **K-Nearest Neighbours** model (`model/msd_knn_model.pkl`) is queried with a feature vector built from:
- Audio centroid (tempo, loudness, mode) corresponding to the detected emotion
- TF-IDF genre text vector from emotion-specific genre tags

The KNN returns the 50 most acoustically similar songs from the local 10,000-song MSD dataset. If the user has favourite or mentioned artists, those rows are boosted to the top. A random sample of 10 is drawn from the top 30 candidates to ensure discovery freshness and variety.

**Path 2 — iTunes Fuzzy Search (Fallback)**

If the KNN model is unavailable (e.g., first run before training), a broad iTunes search query is formed from the emotion's predefined search terms. Artist discovery signals from Last.fm are injected to personalise the query.

Each song from either path is then individually looked up on the iTunes Search API (`https://itunes.apple.com/search`) to retrieve:
- Official album artwork (300×300)
- 30-second MP3/M4A preview stream
- Full Apple Music track URL

---

### 7. Artist Discovery (`spotify/artist_discovery.py`)

When seed artists are available, similar artists are discovered by scraping **Last.fm's public similarity graph** (`/music/{artist}/+similar`). This bypasses the need for a Last.fm API key. Results are shuffled before use to ensure recommendations feel fresh across sessions.

---

### 8. World Music Explorer (`pages/1_World_Music_Explorer.py`)

A dedicated Streamlit page that lets users:
- Upload a photo → CLIP AI scans it for a world landmark
- Or browse 60+ landmarks grouped by continent via a dropdown

Once a landmark is identified, its associated country, language, and genre are displayed alongside a Wikipedia thumbnail. Music is fetched from iTunes using the landmark's genre tags and country storefront code.

---

### 9. Web Interface (`app.py`)

Built with **Streamlit**, using custom CSS with:
- Glassmorphism card design (`backdrop-filter: blur`)
- Dark gradient background (`#090716 → #1a1738`)
- Outfit font (Google Fonts)
- Three-tab input: Camera / Upload / Text
- Three analysis modes: Mood Mirror / Story Vibe / Landmark Locator
- Animated emotion result card with per-emotion color coding
- Session-persistent vibe preferences and genre/artist dialog pickers

---

## Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit + Custom CSS (Glassmorphism) |
| Face Analysis | OpenCV Haar Cascades |
| Text Emotion | scikit-learn TF-IDF + SVM |
| Aesthetic Analysis | OpenCV HSV math (NumPy) |
| Landmark Recognition | HuggingFace CLIP (free public API) |
| Music Ranking | scikit-learn KNN on MSD dataset |
| Music Metadata | Apple iTunes Search API (free, no key) |
| Artist Similarity | Last.fm public scraping (BeautifulSoup) |
| GPS Geocoding | OpenStreetMap Nominatim (free) |
| Image Processing | Pillow |

---

## What Was Removed

This branch (`same-project-no-AI`) represents the fully offline migration. The following were removed:
- ❌ Google Gemini Pro API (`gemini-1.5-pro`) — replaced by local OpenCV + NLP
- ❌ Spotify Web API + Spotipy — replaced by Apple iTunes REST API (no key needed)
- ❌ `google-generativeai` Python SDK — removed from dependencies
