"""
SoulStream — World Music Explorer
===================================
Dedicated page for discovering music from famous world locations.
Upload a photo of any world landmark and get music in that local language & culture.
"""

import streamlit as st
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="World Music Explorer — SoulStream",
    page_icon="🌍",
    layout="centered"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #070b14 0%, #0d1b2a 40%, #0f2236 100%);
        font-family: 'Outfit', sans-serif;
    }
    .main .block-container { padding-top: 2rem; max-width: 850px; }

    .hero {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
    }
    .hero p { color: #7a8fa6; font-size: 1.05rem; margin-top: 5px; }

    .glass {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1.2rem 0;
        backdrop-filter: blur(20px);
    }

    .landmark-card {
        background: linear-gradient(135deg, rgba(67,233,123,0.08), rgba(56,249,215,0.04));
        border: 1px solid rgba(67,233,123,0.25);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .stat-pill {
        display: inline-block;
        background: rgba(67,233,123,0.12);
        border: 1px solid rgba(67,233,123,0.3);
        border-radius: 20px;
        padding: 0.3rem 0.9rem;
        font-size: 0.85rem;
        color: #43e97b;
        margin: 0.2rem 0.2rem 0 0;
    }

    .song-row {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.7rem;
        transition: 0.25s;
    }
    .song-row:hover {
        background: rgba(67,233,123,0.05);
        border-color: rgba(67,233,123,0.2);
    }

    .stButton > button {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        color: #000 !important;
        height: 50px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🌍 World Music Explorer</h1>
    <p>Upload a photo of any famous landmark → get music in that local language & culture</p>
</div>
""", unsafe_allow_html=True)

# ── Also allow browsing landmarks directly ──────────────────────────────────
from model.landmark_detector import LANDMARK_DB

# ── Two input modes ─────────────────────────────────────────────────────────
st.markdown('<div class="glass">', unsafe_allow_html=True)
tab_upload, tab_browse = st.tabs(["📷 Upload Landmark Photo", "🗺️ Browse Famous Places"])

uploaded_img = None
selected_landmark = None

with tab_upload:
    st.write("Upload any photo of a famous world landmark:")
    uploaded_img = st.file_uploader(
        "Upload Landmark Photo",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key="landmark_uploader"
    )
    if uploaded_img:
        from PIL import Image
        img_preview = Image.open(uploaded_img)
        st.image(img_preview, caption="Uploaded Photo", width="stretch")

with tab_browse:
    st.write("Or directly browse from our database of famous world places:")
    # Group landmarks by continent
    CONTINENTS = {
        "Europe": ["Eiffel Tower", "Louvre Museum", "Colosseum", "Leaning Tower of Pisa",
                   "Sagrada Familia", "Big Ben", "Buckingham Palace", "Stonehenge",
                   "Acropolis of Athens", "Neuschwanstein Castle", "Trevi Fountain",
                   "Amsterdam Canals", "Tower of London"],
        "Asia": ["Taj Mahal", "Gateway of India", "India Gate", "Lotus Temple",
                 "Mount Fuji", "Tokyo Tower", "Shibuya Crossing", "Fushimi Inari Shrine",
                 "Gyeongbokgung Palace", "Namsan Tower", "Great Wall of China",
                 "Forbidden City", "Angkor Wat", "Petronas Twin Towers",
                 "Marina Bay Sands", "Burj Khalifa", "Burj Al Arab",
                 "Hagia Sophia", "Blue Mosque", "Petra", "Sphinx", "Pyramids of Giza"],
        "Americas": ["Statue of Liberty", "Empire State Building", "Times Square",
                     "Golden Gate Bridge", "Grand Canyon", "Machu Picchu",
                     "Christ the Redeemer", "Chichen Itza", "Niagara Falls", "CN Tower"],
        "Africa & Oceania": ["Sydney Opera House", "Table Mountain", "Kilimanjaro",
                             "Victoria Falls"],
    }

    continent_choice = st.selectbox("Select Continent", list(CONTINENTS.keys()))
    landmark_choice = st.selectbox("Select Landmark", CONTINENTS[continent_choice])
    info = LANDMARK_DB.get(landmark_choice, {})
    if info:
        st.markdown(f"""
        <div style="margin-top:0.5rem;">
            <span class="stat-pill">🌍 {info['country']}</span>
            <span class="stat-pill">🗣️ {info['language']}</span>
            <span class="stat-pill">🎵 {info['genre']}</span>
        </div>
        """, unsafe_allow_html=True)
    selected_landmark = landmark_choice

discover_clicked = st.button("🎵 Discover Local Music", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Processing ──────────────────────────────────────────────────────────────
if discover_clicked:
    landmark_info = None

    if uploaded_img is not None:
        # Use CLIP AI to detect landmark from photo
        with st.spinner("🤖 AI is scanning your landmark photo..."):
            from model.landmark_detector import recognize_landmark
            result = recognize_landmark(uploaded_img)
            if result.get("detected"):
                landmark_info = result
            else:
                st.warning("Landmark not confidently recognized. Showing results for browsed selection instead.")
                info = LANDMARK_DB.get(selected_landmark, {})
                landmark_info = {
                    "detected": True,
                    "landmark": selected_landmark,
                    "country": info.get("country", "Unknown"),
                    "code": info.get("code", "us"),
                    "language": info.get("language", "English"),
                    "genre": info.get("genre", "pop"),
                    "itunes_country": info.get("code", "us"),
                    "confidence": 100.0
                }
    elif selected_landmark:
        info = LANDMARK_DB.get(selected_landmark, {})
        landmark_info = {
            "detected": True,
            "landmark": selected_landmark,
            "country": info.get("country", "Unknown"),
            "code": info.get("code", "us"),
            "language": info.get("language", "English"),
            "genre": info.get("genre", "pop"),
            "itunes_country": info.get("code", "us"),
            "confidence": 100.0
        }

    if landmark_info and landmark_info.get("detected"):
        # ── Fetch Wikipedia image for the landmark ──
        wiki_img_url = None
        try:
            wiki_r = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(landmark_info['landmark'])}",
                headers={"User-Agent": "SoulStream/1.0"}, timeout=5
            )
            if wiki_r.status_code == 200:
                wiki_img_url = wiki_r.json().get("thumbnail", {}).get("source")
        except Exception:
            pass

        # ── Landmark Result Card ──────────────────────────────────────────
        lcol1, lcol2 = st.columns([1, 2])
        with lcol1:
            if wiki_img_url:
                st.image(wiki_img_url, caption=landmark_info["landmark"], width="stretch")
        with lcol2:
            st.markdown(f"""
            <div class="landmark-card">
                <h3 style="margin:0;color:#43e97b;">🏛️ {landmark_info['landmark']}</h3>
                <p style="color:#fff;font-size:1rem;margin:0.5rem 0 0.2rem 0;">
                    🌍 <b>{landmark_info['country']}</b>
                </p>
                <div style="margin-top:0.5rem;">
                    <span class="stat-pill">🗣️ {landmark_info['language']}</span>
                    <span class="stat-pill">🎵 {landmark_info['genre']}</span>
                    <span class="stat-pill">📡 iTunes: {landmark_info['code'].upper()}</span>
                </div>
                {"<p style='color:#666;font-size:0.8rem;margin-top:0.6rem;'>AI Confidence: " + str(landmark_info.get('confidence','100')) + "%</p>" if uploaded_img else ""}
            </div>
            """, unsafe_allow_html=True)

        # ── Fetch Music from iTunes ────────────────────────────────────────
        st.markdown("### 🎧 Music from This Location")
        import urllib.parse, random

        genre_query = landmark_info["genre"]
        country_code = landmark_info.get("itunes_country", "us")

        with st.spinner(f"Fetching {landmark_info['language']} music from iTunes..."):
            try:
                q = urllib.parse.quote_plus(genre_query)
                url = f"https://itunes.apple.com/search?term={q}&entity=song&limit=30&country={country_code}"
                resp = requests.get(url, timeout=8)
                tracks = resp.json().get("results", []) if resp.status_code == 200 else []
                random.shuffle(tracks)
                tracks = tracks[:10]
            except Exception:
                tracks = []

        if tracks:
            for track in tracks:
                name   = track.get("trackName", "Unknown")
                artist = track.get("artistName", "Unknown")
                album  = track.get("collectionName", "")
                image  = track.get("artworkUrl100", "").replace("100x100bb", "300x300bb")
                preview= track.get("previewUrl", "")
                url_am = track.get("trackViewUrl", "#")

                with st.container():
                    c1, c2 = st.columns([1, 4], vertical_alignment="center")
                    with c1:
                        if image:
                            st.image(image, width="stretch")
                    with c2:
                        st.markdown(f"**{name}**")
                        st.markdown(f"<span style='color:#7a8fa6;font-size:0.9rem;'>{artist} — {album}</span>", unsafe_allow_html=True)
                        if preview:
                            st.audio(preview, format="audio/mp4")
                        if url_am and url_am != "#":
                            st.link_button("🍎 Play Full Song on Apple Music", url_am)
                st.markdown("---")
        else:
            st.info("Could not load songs from iTunes. Try a different region or check your internet connection.")

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#3a4a5a;font-size:0.8rem;padding:2rem;">
    SoulStream World Music Explorer • Powered by CLIP AI & Apple Music
</div>
""", unsafe_allow_html=True)
