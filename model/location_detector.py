"""
SoulStream Location Intelligence Module
========================================
Extracts GPS EXIF from uploaded photos, reverse geocodes to city/country,
maps to iTunes country storefront, and fetches a Wikipedia location image.
"""
import io
import struct
import requests
from PIL import Image, ExifTags

# ── iTunes Country Storefront Codes ──────────────────────────────────
# iTunes API `country` param — maps to local language music catalogs
COUNTRY_TO_ITUNES = {
    "US": "us", "GB": "gb", "IN": "in", "JP": "jp", "KR": "kr",
    "FR": "fr", "DE": "de", "ES": "es", "IT": "it", "MX": "mx",
    "BR": "br", "AR": "ar", "AU": "au", "CA": "ca", "CN": "cn",
    "RU": "ru", "TR": "tr", "SA": "sa", "AE": "ae", "EG": "eg",
    "NG": "ng", "ZA": "za", "TH": "th", "ID": "id", "PH": "ph",
    "PK": "pk", "BD": "bd", "VN": "vn", "MY": "my", "SG": "sg",
    "PL": "pl", "NL": "nl", "SE": "se", "NO": "no", "FI": "fi",
    "PT": "pt", "BE": "be", "CH": "ch", "AT": "at", "GR": "gr",
    "CL": "cl", "CO": "co", "PE": "pe", "VE": "ve", "KE": "ke",
}

# ── Country Flags (emoji) ─────────────────────────────────────────────
def country_flag(code: str) -> str:
    """Convert ISO country code to flag emoji."""
    code = code.upper()
    if len(code) != 2:
        return ""
    return chr(0x1F1E6 + ord(code[0]) - ord('A')) + chr(0x1F1E6 + ord(code[1]) - ord('A'))

# ── Language Display Names ────────────────────────────────────────────
COUNTRY_LANGUAGE = {
    "US": "English", "GB": "English", "IN": "Hindi / Regional",
    "JP": "Japanese", "KR": "Korean", "FR": "French", "DE": "German",
    "ES": "Spanish", "IT": "Italian", "MX": "Spanish", "BR": "Portuguese",
    "AR": "Spanish", "AU": "English", "CA": "English/French",
    "CN": "Mandarin", "RU": "Russian", "TR": "Turkish", "SA": "Arabic",
    "AE": "Arabic", "EG": "Arabic", "NG": "Afrobeats/English",
    "ZA": "Afrikaans/English", "TH": "Thai", "ID": "Indonesian",
    "PH": "Filipino/English", "PK": "Urdu", "BD": "Bengali",
    "VN": "Vietnamese", "MY": "Malay", "SG": "English/Mandarin",
}

# ── EXIF GPS Extraction ───────────────────────────────────────────────
def _get_decimal_coords(coords, ref):
    decimal = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_gps_from_image(image_input) -> tuple | None:
    """Returns (latitude, longitude) from image EXIF, or None if not available."""
    try:
        if isinstance(image_input, Image.Image):
            img = image_input
        else:
            img = Image.open(image_input)

        exif_data = img._getexif()
        if not exif_data:
            return None

        exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
        gps_info_raw = exif.get("GPSInfo")
        if not gps_info_raw:
            return None

        gps = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps_info_raw.items()}
        lat = _get_decimal_coords(gps["GPSLatitude"], gps["GPSLatitudeRef"])
        lon = _get_decimal_coords(gps["GPSLongitude"], gps["GPSLongitudeRef"])
        return lat, lon
    except Exception:
        return None

# ── Reverse Geocoding ────────────────────────────────────────────────
def reverse_geocode(lat: float, lon: float) -> dict:
    """Returns city, country_code from coordinates using offline reverse_geocoder."""
    try:
        import reverse_geocoder as rg
        results = rg.search((lat, lon), verbose=False)
        if results:
            r = results[0]
            return {
                "city": r.get("name", "Unknown"),
                "country_code": r.get("cc", "US"),
                "region": r.get("admin1", "")
            }
    except Exception:
        pass
    return {"city": "Unknown", "country_code": "US", "region": ""}

# ── Wikipedia Location Image ─────────────────────────────────────────
def fetch_location_image(city: str, country_code: str = "") -> str | None:
    """Fetches a representative Wikipedia thumbnail for the detected location."""
    try:
        query = city
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(query)}"
        r = requests.get(url, timeout=5, headers={"User-Agent": "SoulStream/1.0"})
        if r.status_code == 200:
            data = r.json()
            thumbnail = data.get("thumbnail", {}).get("source")
            if thumbnail:
                return thumbnail
    except Exception:
        pass
    return None


# ── Main Entry Point ─────────────────────────────────────────────────
def detect_location(image_input) -> dict:
    """
    Full pipeline:
    1. Extract GPS from EXIF
    2. Reverse geocode to city/country
    3. Map to iTunes storefront + language
    4. Fetch Wikipedia thumbnail

    Returns a dict with: city, country_code, itunes_country,
                          language, flag, wiki_image (or None)
    """
    coords = extract_gps_from_image(image_input)
    if not coords:
        return {"detected": False}

    lat, lon = coords
    geo = reverse_geocode(lat, lon)
    country_code = geo.get("country_code", "US")
    city = geo.get("city", "Unknown")
    region = geo.get("region", "")

    flag = country_flag(country_code)
    language = COUNTRY_LANGUAGE.get(country_code, "Local")
    itunes_country = COUNTRY_TO_ITUNES.get(country_code, "us")
    wiki_image = fetch_location_image(city, country_code)

    return {
        "detected": True,
        "lat": lat,
        "lon": lon,
        "city": city,
        "region": region,
        "country_code": country_code,
        "flag": flag,
        "language": language,
        "itunes_country": itunes_country,
        "wiki_image": wiki_image,
        "display": f"{flag} {city}, {country_code}"
    }
