"""
🎵 SoulStream
Streamlit application — detects emotion via camera/text and recommends Spotify songs.
"""

import streamlit as st
import sys
import os
from PIL import Image

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spotify.history_manager import load_history, add_artist, DEFAULT_GENRES

# ─── Discovery Dialogs ─────────────────────────────────────
@st.dialog("Select Artist")
def show_artist_dialog():
    history = load_history()
    artists = history.get("artists", [])
    if not artists:
        st.write("No artists discovered yet.")
    else:
        selected = st.selectbox("Famous Artists", artists)
        if st.button("Add"):
            current_vibe = st.session_state.get('user_vibe_input', '')
            st.session_state.user_vibe_input = f"{current_vibe} {selected}".strip()
            st.rerun()

@st.dialog("Select Genre")
def show_genre_dialog():
    selected = st.selectbox("Music Genres", DEFAULT_GENRES)
    if st.button("Add"):
        st.session_state.selected_genre = selected
        current_vibe = st.session_state.get('user_vibe_input', '')
        st.session_state.user_vibe_input = f"{current_vibe} {selected}".strip()
        st.rerun()

# ─── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="SoulStream",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if 'user_vibe_input' not in st.session_state:
    st.session_state.user_vibe_input = ""
if 'selected_genre' not in st.session_state:
    st.session_state.selected_genre = None

# ─── Sidebar Settings ──────────────────────────────────────
with st.sidebar:
    st.title("⚙️ SoulStream Settings")
    simplified_ui = st.toggle("Simplified UI", value=True)
    open_top_pick = st.toggle("Show 'Open Top Pick' Button", value=True)
    
    st.markdown("---")
    st.markdown("### 🧬 Personalization")
    target_artists = st.multiselect(
        "Focus on these artists:",
        ["The Weeknd", "Drake", "Taylor Swift", "Billie Eilish", "Dua Lipa", "Travis Scott", "Eminem", "Kendrick Lamar", "Adele"],
        default=["The Weeknd"]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("SoulStream detects your mood from your face or text and recommends music via Apple Music. Fully offline & powered by local ML.")

    # ─── Location / Language ───
    st.markdown("---")
    st.markdown("### 🌍 Music Region")
    st.caption("Select your region to get music in your local language. Auto-detected from photo GPS when available.")
    REGION_OPTIONS = {
        "🌐 Global (English)": "us",
        "🇮🇳 India (Hindi/Regional)": "in",
        "🇯🇵 Japan (Japanese)": "jp",
        "🇰🇷 South Korea (Korean)": "kr",
        "🇧🇷 Brazil (Portuguese)": "br",
        "🇲🇽 Mexico (Spanish)": "mx",
        "🇫🇷 France (French)": "fr",
        "🇩🇪 Germany (German)": "de",
        "🇪🇸 Spain (Spanish)": "es",
        "🇮🇹 Italy (Italian)": "it",
        "🇷🇺 Russia (Russian)": "ru",
        "🇹🇷 Turkey (Turkish)": "tr",
        "🇸🇦 Saudi Arabia (Arabic)": "sa",
        "🇨🇳 China (Mandarin)": "cn",
        "🇵🇭 Philippines (Filipino)": "ph",
        "🇮🇩 Indonesia (Indonesian)": "id",
        "🇳🇬 Nigeria (Afrobeats)": "ng",
        "🇿🇦 South Africa": "za",
        "🇦🇺 Australia": "au",
        "🇬🇧 United Kingdom": "gb",
        "🇨🇦 Canada": "ca",
    }
    selected_region_label = st.selectbox(
        "Music Region",
        list(REGION_OPTIONS.keys()),
        index=0,
        label_visibility="collapsed"
    )
    manual_itunes_country = REGION_OPTIONS[selected_region_label]

    # ─── Discovery Section ───
    st.markdown("---")
    st.subheader("🔎 Discovery")
    if st.button("🎙️ Browse Artists"):
        show_artist_dialog()
    if st.button("🎨 Browse Genres"):
        show_genre_dialog()

# ─── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #090716 0%, #110e2d 40%, #1a1738 100%);
        font-family: 'Outfit', sans-serif;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }

    .hero-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .hero-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }

    .hero-header p {
        color: #8b8fa3;
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 5px;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }

    .emotion-result {
        text-align: center;
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        animation: fadeInUp 0.6s ease-out;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .emotion-emoji {
        font-size: 5rem;
        display: block;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));
    }

    .emotion-label {
        font-size: 2rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin: 0.5rem 0;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        color: white;
        padding: 0 20px;
        transition: all 0.3s;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(255,255,255,0.15) !important;
        border-bottom-color: #f5576c !important;
    }

    /* Input styling */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Rebranding colors */
    .stButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 50px !important;
    }

    .song-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        transition: 0.3s;
    }

    .song-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>SoulStream</h1>
    <p>Music that matches your soul • Powered by Local AI</p>
</div>
""", unsafe_allow_html=True)

# ─── Input Section ─────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

st.write("### 🎛️ Analysis Engine")
analysis_mode = st.radio(
    "Select how SoulStream should interpret your photo:",
    options=[
        "🎭 Mood Mirror (Facial Emotion)",
        "📸 Instagram Story Vibe (Whole Image Analysis)",
        "🏙️ Landmark Locator (Identify Famous Places)"
    ],
    index=0
)
st.write("---")

input_tab_camera, input_tab_upload, input_tab_text = st.tabs(["📸 Camera Mode", "📂 Upload Mode", "⌨️ Text Mode"])

with input_tab_camera:
    st.write("Capture your expression to detect your mood:")
    camera_photo = st.camera_input("Capture Heartbeat", label_visibility="collapsed")

with input_tab_upload:
    st.write("Upload a photo (Face or Aesthetic Scene) to extract the vibe:")
    upload_photo = st.file_uploader("Upload Photo", type=['png', 'jpg', 'jpeg', 'webp'], label_visibility="collapsed")

with input_tab_text:
    user_text = st.text_area(
        "How are you feeling?",
        placeholder="Type your mood... e.g., 'Feeling a bit nostalgic tonight'",
        height=100,
        label_visibility="collapsed",
        key="user_text_input_area"
    )

st.write("### 💎 Your Permanent Vibe")
vibe_pref = st.text_input(
    "Preferred Artists or Genres (e.g., The Weeknd, Lofi, Synth-pop)",
    value=st.session_state.user_vibe_input,
    placeholder="These will be remembered for your entire session...",
    key="user_vibe_input_persistent"
)
st.session_state.user_vibe_input = vibe_pref

analyze_clicked = st.button("🚀 Stream My Music", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── Processing ────────────────────────────────────────────
predict_source = None
img_file = None

if upload_photo:
    predict_source = "camera"
    img_file = upload_photo
elif camera_photo:
    predict_source = "camera"
    img_file = camera_photo
elif analyze_clicked:
    if user_text:
        predict_source = "text"
    else:
        st.warning("Please capture/upload a photo or enter text first!")

if predict_source:
    with st.spinner("✨ SoulStream is reading your vibe..."):
        try:
            from model.vision import analyze_face
            from model.predict import predict_emotion
            from spotify.recommender import get_recommendations
            from model.location_detector import detect_location

            # ── Location Intelligence ──
            location_info = {"detected": False}
            itunes_country = manual_itunes_country  # Default to manual selection
            if img_file is not None:
                location_info = detect_location(img_file)
                if location_info.get("detected"):
                    # GPS auto-detected — override manual selection
                    itunes_country = location_info.get("itunes_country", manual_itunes_country)
                else:
                    # No GPS in photo — use manual region silently
                    location_info["detected"] = False

            result = None
            landmark_info = {"detected": False}

            if predict_source == "camera":
                if "Story Vibe" in analysis_mode:
                    from model.story_vibe import analyze_story_vibe
                    result = analyze_story_vibe(img_file)
                elif "Landmark" in analysis_mode:
                    from model.landmark_detector import recognize_landmark
                    with st.spinner("🏙️ Scanning for world landmarks via AI..."):
                        landmark_info = recognize_landmark(img_file)
                    if not landmark_info.get("detected"):
                        # Fall back to story vibe if landmark not recognized
                        from model.story_vibe import analyze_story_vibe
                        result = analyze_story_vibe(img_file)
                    else:
                        # Use a neutral aesthetic emotion as base, genre will be overridden
                        result = {
                            "emotion": "aesthetic",
                            "musical_keywords": landmark_info["genre"].split(),
                            "mentioned_artists": [],
                            "confidence": landmark_info["confidence"] / 100,
                            "emoji": "🏙️",
                            "color": "#e1306c",
                            "all_scores": {"aesthetic": landmark_info["confidence"] / 100},
                            "reasoning": f"Landmark detected: {landmark_info['landmark']}, {landmark_info['country']}"
                        }
                        itunes_country = landmark_info.get("itunes_country", itunes_country)
                else:
                    result = analyze_face(img_file)
            else:
                result = predict_emotion(user_text)

            if result.get("error"):
                st.error(f"❌ {result['error']}")
            else:
                emotion = result["emotion"]
                keywords = result.get("musical_keywords", [])
                mentioned_artists = result.get("mentioned_artists", [])
                confidence = result["confidence"]
                emoji = result["emoji"]
                color = result["color"]
                all_scores = result["all_scores"]
                reasoning = result.get("reasoning", "")

                # ── Emotion Result Card ──
                st.markdown(f"""
                <div class="emotion-result glass-card" style="border-right: 10px solid {color}; border-left: 10px solid {color};">
                    <span class="emotion-emoji">{emoji}</span>
                    <div class="emotion-label" style="color: {color};">{emotion}</div>
                    <p style="color: #a8adc0; font-style: italic;">"{reasoning or 'Detected based on your input'}"</p>
                </div>
                """, unsafe_allow_html=True)

                # ── Location Intelligence Card ──
                if location_info.get("detected"):
                    loc_col1, loc_col2 = st.columns([1, 3])
                    with loc_col1:
                        if location_info.get("wiki_image"):
                            st.image(location_info["wiki_image"], caption=location_info.get("city", ""), width='stretch')
                    with loc_col2:
                        st.markdown(f"""
                        <div class="glass-card" style="padding:1rem;">
                            <h4 style="margin:0;color:#e1306c;">{location_info.get('flag','')} Location Detected</h4>
                            <p style="color:#fff;font-size:1.1rem;margin:0.3rem 0;"><b>{location_info.get('city','')}, {location_info.get('country_code','')}</b></p>
                            <p style="color:#a8adc0;margin:0;">Language: {location_info.get('language','Local')} &nbsp;|&nbsp; Routing iTunes to <b>{location_info.get('country_code','').upper()}</b> storefront</p>
                        </div>
                        """, unsafe_allow_html=True)

                # ── Landmark Card ──
                if landmark_info.get("detected"):
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 6px solid #e1306c; padding: 1.2rem;">
                        <h4 style="margin:0 0 0.4rem 0; color:#e1306c;">🏙️ Landmark Identified</h4>
                        <p style="color:#fff; font-size:1.15rem; margin:0;"><b>{landmark_info['landmark']}</b></p>
                        <p style="color:#a8adc0; margin:0.3rem 0 0 0;">
                            🌍 {landmark_info['country']} &nbsp;•&nbsp;
                            🗣️ Language: <b>{landmark_info['language']}</b> &nbsp;•&nbsp;
                            🎧 Genre: <b>{landmark_info['genre']}</b>
                        </p>
                        <p style="color:#666; font-size:0.8rem; margin:0.4rem 0 0 0;">AI Confidence: {landmark_info['confidence']}% • iTunes routed to {landmark_info['code'].upper()} storefront</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Recommendations ──
                st.markdown("### 🎧 Soul-Matched Tracks")
                
                # Merge vibe preferences
                personal_context = f"{vibe_pref} {st.session_state.get('selected_genre', '')}".strip()
                
                recs = get_recommendations(
                    emotion,
                    keywords=keywords,
                    itunes_country=itunes_country,
                    favorite_artists=target_artists,
                    mentioned_artists=mentioned_artists,
                    genre=st.session_state.get('selected_genre'),
                    context_text=personal_context, # Passing our new persistent vibe
                    limit=10
                )

                if recs.get("songs"):
                    for song in recs["songs"]:
                        add_artist(song.get("artist", ""))
                        
                        with st.container():
                            col1, col2 = st.columns([1, 4], vertical_alignment="center")
                            with col1:
                                if song.get("image"): 
                                    st.image(song["image"], width='stretch')
                            with col2:
                                st.markdown(f"**{song['name']}**")
                                st.markdown(f"<span style='color: #a8adc0; font-size: 0.9rem;'>{song['artist']}</span>", unsafe_allow_html=True)
                                
                                # Native HTML5 Audio Player (iTunes Preview stream)
                                if song.get("preview"):
                                    st.audio(song["preview"], format="audio/mp4")
                                
                                # Always provide the outbound link to the official full track!
                                if song.get("url") and song["url"] != "#":
                                    st.link_button("🎵 Play Full Song on Apple Music", song["url"])
                        st.markdown("---")
                else:
                    st.info("No network connection or songs found for this vibe. Try adjusting your preferences!")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("""
<div style="text-align: center; color: #4a4e60; font-size: 0.8rem; padding: 2rem;">
    SoulStream • Built with offline ML models & Spotify API
</div>
""", unsafe_allow_html=True)
