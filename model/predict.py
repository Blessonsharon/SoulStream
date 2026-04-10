import os
import re
import pickle
from model.dataset import MUSICAL_KEYWORDS_MAP, KNOWN_ARTISTS

# Expanded Granular Taxonomy
EMOTION_EMOJIS = {
    "happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐",
    "party": "🪩", "lust": "💋", "hangover": "🤕", "breakup": "💔", 
    "depression": "🌧️", "lonely": "🧍", "stressed": "😫", "anxiety": "😟", 
    "adrenaline rush": "🏎️", "gym": "🏋️", "athletic": "🏆", "love": "❤️"
}

EMOTION_COLORS = {
    "happy": "#FFD700", "sad": "#4A90D9", "angry": "#E74C3C", "neutral": "#95A5A6",
    "party": "#ff006e", "lust": "#c1121f", "hangover": "#a3b18a", "breakup": "#14213d", 
    "depression": "#2b2d42", "lonely": "#5c677d", "stressed": "#f4a261", "anxiety": "#e9c46a", 
    "adrenaline rush": "#e63946", "gym": "#fca311", "athletic": "#3a86ff", "love": "#ffb703"
}

# The Zero-Shot NLP Matrix Dictionary
# This maps explicit raw conversation phrases immediately to exact hyper-specific moods.
EXPLICIT_MOOD_DICTIONARY = {
    "party": [r'\bparty\b', r'\bclubbing\b', r'\brave\b', r'\bdance\b', r'\bgoing out\b', r'\blive it up\b'],
    "lust": [r'\blust\b', r'\bhookup\b', r'\bintimate\b', r'\btogether\b', r'\bromance\b', r'\bsexy\b'],
    "hangover": [r'\bhangover\b', r'\bhungover\b', r'\bdrank too much\b', r'\bheadache\b', r'\bpuking\b', r'\bwasted\b'],
    "breakup": [r'\bbreakup\b', r'\bbroke up\b', r'\bdumped\b', r'\bheartbreak\b', r'\bleft me\b', r'\bcheated\b'],
    "depression": [r'\bdepression\b', r'\bdepressed\b', r'\bgive up\b', r'\bhollow\b', r'\bnumb\b', r'\bsuicidal\b'],
    "lonely": [r'\blonely\b', r'\balone\b', r'\bmiss them\b', r'\bno friends\b', r'\bisolated\b'],
    "stressed": [r'\bstressed\b', r'\btoo much work\b', r'\boverwhelmed\b', r'\bexhausted\b', r'\bdeadline\b'],
    "anxiety": [r'\banxiety\b', r'\banxious\b', r'\bpanic\b', r'\bnervous\b', r'\bfreaking out\b'],
    "adrenaline rush": [r'\badrenaline\b', r'\bhype\b', r'\bmax out\b', r'\bcrazy energy\b', r'\bgod mode\b'],
    "gym": [r'\bgym\b', r'\bworkout\b', r'\blifting\b', r'\bpump\b', r'\bweights\b'],
    "athletic": [r'\bsports\b', r'\bgame day\b', r'\bmatch\b', r'\brunning\b', r'\bsprint\b'],
    "love": [r'\blove\b', r'\bin love\b', r'\bsoulmate\b', r'\bhappily married\b', r'\bmy partner\b']
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "local_text_model.pkl")
_local_model = None

def load_or_train_model():
    global _local_model
    if _local_model is not None:
        return _local_model
    try:
        from model.train_text_model import train_and_save_model
        if not os.path.exists(MODEL_PATH):
            train_and_save_model()
        with open(MODEL_PATH, "rb") as f:
            _local_model = pickle.load(f)
    except Exception as e:
        print(f"Warning: Could not load or train model: {e}")
        _local_model = None
    return _local_model

def extract_artists(text: str) -> list:
    """Simple dictionary lookup to extract known artists."""
    found = []
    text_lower = text.lower()
    for artist in KNOWN_ARTISTS:
        if re.search(r'\b' + re.escape(artist.lower()) + r'\b', text_lower):
            found.append(artist)
    return found

def zero_shot_classification(text: str) -> str:
    """Scans the text for hyper-specific emotion keywords to bypass generic ML."""
    text_lower = text.lower()
    for mood, patterns in EXPLICIT_MOOD_DICTIONARY.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return mood
    return None

def predict_emotion(text: str) -> dict:
    if not text or not text.strip():
        return {"emotion": None, "confidence": 0.0, "emoji": "❓", "color": "#666666", "all_scores": {}, "error": "Please enter text."}
    
    # ── Tier 1: Hyper-Granular Zero-Shot Filter ──
    explicit_mood = zero_shot_classification(text)
    mentioned_artists = extract_artists(text)
    
    if explicit_mood:
        return {
            "emotion": explicit_mood,
            "musical_keywords": [],  # Let recommender.py handle the specialized mapping
            "mentioned_artists": mentioned_artists,
            "confidence": 0.99,
            "emoji": EMOTION_EMOJIS.get(explicit_mood, "🤔"),
            "color": EMOTION_COLORS.get(explicit_mood, "#666666"),
            "all_scores": {explicit_mood: 0.99, "happy": 0.01, "sad": 0.01, "angry": 0.01, "neutral": 0.01},
            "reasoning": f"Zero-Shot NLP explicitly identified complex state: {explicit_mood.capitalize()}."
        }

    # ── Tier 2: Machine Learning Generic Fallback ──
    model = load_or_train_model()
    if not model:
        return {"emotion": None, "error": "Local text model failed to initialize."}
        
    try:
        predicted_class = model.predict([text])[0]
        probas = model.predict_proba([text])[0]
        classes = model.classes_
        
        all_scores = {cls: float(prob) for cls, prob in zip(classes, probas)}
        confidence = float(all_scores.get(predicted_class, 0.0))
        musical_keywords = MUSICAL_KEYWORDS_MAP.get(predicted_class, [])
        
        return {
            "emotion": predicted_class,
            "musical_keywords": musical_keywords,
            "mentioned_artists": mentioned_artists,
            "confidence": confidence,
            "emoji": EMOTION_EMOJIS.get(predicted_class, "🤔"),
            "color": EMOTION_COLORS.get(predicted_class, "#666666"),
            "all_scores": all_scores,
            "reasoning": "Machine Learning mapped general sentiment patterns."
        }
    except Exception as e:
        return {"emotion": None, "error": f"Local Text Model Error: {str(e)}"}
