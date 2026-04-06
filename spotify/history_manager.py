import json
import os

# Path to the JSON file that stores user history
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "history.json")

# Predefined list of common genres (can be extended later)
DEFAULT_GENRES = [
    "Pop",
    "Rock",
    "Hip‑Hop",
    "Jazz",
    "Classical",
    "Bollywood",
    "Tamil",
    "Electronic",
    "R&B",
    "Country",
]

def _ensure_file_exists():
    """Create the history file with default structure if it does not exist."""
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"artists": [], "genres": DEFAULT_GENRES}, f, ensure_ascii=False, indent=2)

def load_history():
    """Load the history JSON and return a dict with 'artists' and 'genres'."""
    _ensure_file_exists()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(history):
    """Write the provided history dict back to the JSON file."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_artist(artist_name: str):
    """Add a new artist to the persisted list if not already present."""
    if not artist_name:
        return
    history = load_history()
    artists = history.get("artists", [])
    if artist_name not in artists:
        artists.append(artist_name)
        history["artists"] = artists
        save_history(history)

def add_genre(genre_name: str):
    """Add a new genre to the persisted list (optional, not used currently)."""
    if not genre_name:
        return
    history = load_history()
    genres = history.get("genres", [])
    if genre_name not in genres:
        genres.append(genre_name)
        history["genres"] = genres
        save_history(history)
