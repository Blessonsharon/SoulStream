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
    player_mode = st.radio("Player Style", ["Embedded Player", "Compact List"], index=0)
    
    st.markdown("---")
    st.markdown("### 🧬 Personalization")
    target_artists = st.multiselect(
        "Focus on these artists:",
        ["The Weeknd", "Drake", "Taylor Swift", "Billie Eilish", "Dua Lipa", "Travis Scott", "Eminem", "Kendrick Lamar", "Adele"],
        default=["The Weeknd"]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("SoulStream captures your facial expression to understand your mood and recommends perfect Spotify tracks.")

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
    <p>Music that matches your soul • Powered by Gemini Vision</p>
</div>
""", unsafe_allow_html=True)

# ─── Input Section ─────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

input_tab_camera, input_tab_text = st.tabs(["📸 Camera Mode", "⌨️ Text Mode"])

with input_tab_camera:
    st.write("Capture your expression to detect your mood:")
    camera_photo = st.camera_input("Capture Heartbeat", label_visibility="collapsed")

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

if camera_photo:
    predict_source = "camera"
    img_file = camera_photo
elif analyze_clicked:
    if user_text:
        predict_source = "text"
    elif not camera_photo:
        st.warning("⚠️ Please capture a photo or enter text to detect your mood!")

if predict_source:
    with st.spinner("✨ SoulStream is reading your vibe..."):
        try:
            from model.vision import analyze_face
            from model.predict import predict_emotion
            from spotify.recommender import get_recommendations

            result = None
            if predict_source == "camera":
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

                # ── Recommendations ──
                st.markdown("### 🎧 Soul-Matched Tracks")
                
                # Merge vibe preferences
                personal_context = f"{vibe_pref} {st.session_state.get('selected_genre', '')}".strip()
                
                recs = get_recommendations(
                    emotion,
                    keywords=keywords,
                    favorite_artists=target_artists,
                    mentioned_artists=mentioned_artists,
                    genre=st.session_state.get('selected_genre'),
                    context_text=personal_context, # Passing our new persistent vibe
                    limit=10
                )

                if recs.get("songs"):
                    for song in recs["songs"]:
                        add_artist(song.get("artist", ""))
                        if player_mode == "Embedded Player" and song.get("id"):
                            embed_url = f"https://open.spotify.com/embed/track/{song['id']}?utm_source=generator&theme=0"
                            st.components.v1.iframe(embed_url, height=80, scrolling=False)
                        else:
                            with st.container():
                                col1, col2, col3 = st.columns([1, 4, 1.5], vertical_alignment="center")
                                with col1:
                                    if song.get("image"): st.image(song["image"])
                                with col2:
                                    st.write(f"**{song['name']}**")
                                    st.write(f"<span style='color: grey; font-size: 0.8rem;'>{song['artist']}</span>", unsafe_allow_html=True)
                                with col3:
                                    if song["url"] != "#": st.link_button("Play", song["url"])
                                st.markdown("---")
                else:
                    st.info("No songs found for this vibe. Try adjusting your preferences!")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("""
<div style="text-align: center; color: #4a4e60; font-size: 0.8rem; padding: 2rem;">
    SoulStream • Built with Google Gemini & Spotify API
</div>
""", unsafe_allow_html=True)
