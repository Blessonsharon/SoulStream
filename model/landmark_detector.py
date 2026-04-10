"""
SoulStream Landmark Intelligence Module
=========================================
Uses HuggingFace CLIP zero-shot image classification (free, no API key)
to identify famous world landmarks from photos, then maps them to:
  - Country & Language
  - Culturally relevant music genre
  - iTunes country storefront
"""
import io
import base64
import requests
from PIL import Image

# ── Famous Landmark Database ─────────────────────────────────────────
# Maps landmark name → country info + culturally relevant music genre
LANDMARK_DB = {
    # Europe
    "Eiffel Tower":             {"country": "France",        "code": "fr", "language": "French",    "genre": "french chanson romantic pop"},
    "Louvre Museum":            {"country": "France",        "code": "fr", "language": "French",    "genre": "french classical ambient art"},
    "Colosseum":                {"country": "Italy",         "code": "it", "language": "Italian",   "genre": "italian opera romantic"},
    "Leaning Tower of Pisa":    {"country": "Italy",         "code": "it", "language": "Italian",   "genre": "italian pop folk"},
    "Sagrada Familia":          {"country": "Spain",         "code": "es", "language": "Spanish",   "genre": "flamenco spanish pop"},
    "Big Ben":                  {"country": "UK",            "code": "gb", "language": "English",   "genre": "british indie rock pop"},
    "Buckingham Palace":        {"country": "UK",            "code": "gb", "language": "English",   "genre": "british classical orchestral"},
    "Stonehenge":               {"country": "UK",            "code": "gb", "language": "English",   "genre": "celtic folk ambient"},
    "Acropolis of Athens":      {"country": "Greece",        "code": "gr", "language": "Greek",     "genre": "greek folk laika"},
    "Neuschwanstein Castle":    {"country": "Germany",       "code": "de", "language": "German",    "genre": "german classical folk ambient"},
    "Colosseum Rome":           {"country": "Italy",         "code": "it", "language": "Italian",   "genre": "italian opera classical"},
    "Trevi Fountain":           {"country": "Italy",         "code": "it", "language": "Italian",   "genre": "italian romantic pop"},
    "Amsterdam Canals":         {"country": "Netherlands",   "code": "nl", "language": "Dutch",     "genre": "dutch electronic chill"},
    "Pantheon":                 {"country": "France",        "code": "fr", "language": "French",    "genre": "french orchestral classical"},
    "Tower of London":          {"country": "UK",            "code": "gb", "language": "English",   "genre": "british rock alternative"},

    # Asia
    "Taj Mahal":                {"country": "India",         "code": "in", "language": "Hindi",     "genre": "bollywood classical romantic"},
    "Gateway of India":         {"country": "India",         "code": "in", "language": "Hindi",     "genre": "bollywood dance pop"},
    "India Gate":               {"country": "India",         "code": "in", "language": "Hindi",     "genre": "indian classical patriotic"},
    "Lotus Temple":             {"country": "India",         "code": "in", "language": "Hindi",     "genre": "indian meditation spiritual"},
    "Mount Fuji":               {"country": "Japan",         "code": "jp", "language": "Japanese",  "genre": "japanese ambient folk calm"},
    "Tokyo Tower":              {"country": "Japan",         "code": "jp", "language": "Japanese",  "genre": "j-pop electronic city pop"},
    "Shibuya Crossing":         {"country": "Japan",         "code": "jp", "language": "Japanese",  "genre": "j-pop hip hop urban"},
    "Fushimi Inari Shrine":     {"country": "Japan",         "code": "jp", "language": "Japanese",  "genre": "japanese traditional calm"},
    "Gyeongbokgung Palace":     {"country": "South Korea",   "code": "kr", "language": "Korean",    "genre": "k-pop traditional korean"},
    "Namsan Tower":             {"country": "South Korea",   "code": "kr", "language": "Korean",    "genre": "k-pop romantic kpop"},
    "Great Wall of China":      {"country": "China",         "code": "cn", "language": "Mandarin",  "genre": "chinese folk traditional canto"},
    "Forbidden City":           {"country": "China",         "code": "cn", "language": "Mandarin",  "genre": "chinese classical orchestral"},
    "Angkor Wat":               {"country": "Cambodia",      "code": "us", "language": "Khmer",     "genre": "southeast asian ambient folk"},
    "Petronas Twin Towers":     {"country": "Malaysia",      "code": "my", "language": "Malay",     "genre": "malay pop rnb"},
    "Marina Bay Sands":         {"country": "Singapore",     "code": "sg", "language": "English",   "genre": "singapore pop electronic"},
    "Burj Khalifa":             {"country": "UAE",           "code": "ae", "language": "Arabic",    "genre": "arabic khaleeji pop"},
    "Burj Al Arab":             {"country": "UAE",           "code": "ae", "language": "Arabic",    "genre": "arabic luxury lounge"},
    "Hagia Sophia":             {"country": "Turkey",        "code": "tr", "language": "Turkish",   "genre": "turkish pop arabesk"},
    "Blue Mosque":              {"country": "Turkey",        "code": "tr", "language": "Turkish",   "genre": "turkish folk traditional"},
    "Petra":                    {"country": "Jordan",        "code": "us", "language": "Arabic",    "genre": "arabic desert ambient folk"},
    "Sphinx":                   {"country": "Egypt",         "code": "eg", "language": "Arabic",    "genre": "arabic egyptian pop shaabi"},
    "Pyramids of Giza":         {"country": "Egypt",         "code": "eg", "language": "Arabic",    "genre": "arabic classical folk egyptian"},

    # Americas
    "Statue of Liberty":        {"country": "USA",           "code": "us", "language": "English",   "genre": "american pop hip hop rock"},
    "Empire State Building":    {"country": "USA",           "code": "us", "language": "English",   "genre": "new york hip hop jazz"},
    "Times Square":             {"country": "USA",           "code": "us", "language": "English",   "genre": "pop hiphop urban electronic"},
    "Golden Gate Bridge":       {"country": "USA",           "code": "us", "language": "English",   "genre": "west coast hip hop indie"},
    "Grand Canyon":             {"country": "USA",           "code": "us", "language": "English",   "genre": "americana folk rock"},
    "Machu Picchu":             {"country": "Peru",          "code": "pe", "language": "Spanish",   "genre": "latin andean folk"},
    "Christ the Redeemer":      {"country": "Brazil",        "code": "br", "language": "Portuguese","genre": "samba bossa nova brazilian pop"},
    "Colosseum Brazil":         {"country": "Brazil",        "code": "br", "language": "Portuguese","genre": "brazilian funk samba"},
    "Chichen Itza":             {"country": "Mexico",        "code": "mx", "language": "Spanish",   "genre": "mexican folk mariachi"},
    "Niagara Falls":            {"country": "Canada",        "code": "ca", "language": "English",   "genre": "canadian indie rock pop"},
    "CN Tower":                 {"country": "Canada",        "code": "ca", "language": "English",   "genre": "canadian pop hip hop"},

    # Africa & Oceania
    "Sydney Opera House":       {"country": "Australia",     "code": "au", "language": "English",   "genre": "australian indie pop rock"},
    "Table Mountain":           {"country": "South Africa",  "code": "za", "language": "Afrikaans", "genre": "south african afrobeats kwaito"},
    "Kilimanjaro":              {"country": "Tanzania",      "code": "us", "language": "Swahili",   "genre": "african afrobeats folk"},
    "Victoria Falls":           {"country": "Zimbabwe",      "code": "za", "language": "Shona",     "genre": "african traditional folk"},
}

CANDIDATE_LABELS = list(LANDMARK_DB.keys())


def _image_to_bytes(image_input) -> bytes:
    if isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        img = Image.open(image_input).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return buf.getvalue()


def recognize_landmark(image_input) -> dict:
    """
    Sends the image to HuggingFace CLIP zero-shot classification API.
    Returns the best-matching landmark with country/language/genre info.
    """
    try:
        image_bytes = _image_to_bytes(image_input)
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # HuggingFace CLIP zero-shot image classification (free, public)
        API_URL = "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32"
        payload = {
            "inputs": {"image": img_b64},
            "parameters": {"candidate_labels": CANDIDATE_LABELS}
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)

        if response.status_code == 200:
            results = response.json()
            # HF returns list of {label, score}
            if isinstance(results, list) and results:
                # Sort by confidence score descending
                results.sort(key=lambda x: x.get("score", 0), reverse=True)
                best = results[0]
                landmark_name = best.get("label", "")
                confidence = best.get("score", 0)

                # Only accept if confidence is reasonably high
                if confidence > 0.05 and landmark_name in LANDMARK_DB:
                    info = LANDMARK_DB[landmark_name]
                    return {
                        "detected": True,
                        "landmark": landmark_name,
                        "country": info["country"],
                        "code": info["code"],
                        "language": info["language"],
                        "genre": info["genre"],
                        "itunes_country": info["code"],
                        "confidence": round(confidence * 100, 1),
                        "display": f"{landmark_name}, {info['country']}"
                    }

    except Exception as e:
        print(f"Landmark recognition error: {e}")

    return {"detected": False}
