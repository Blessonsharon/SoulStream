"""
🎵 SoulStream
Streamlit application — detects emotion via camera/text and recommends Spotify songs.
"""

import streamlit as st
import sys
import os
from PIL import Image

# Load tsParticles local library for offline background effects
try:
    with open("tsparticles.min.js", "r", encoding="utf-8") as f:
        tsparticles_js = f.read()
except Exception:
    tsparticles_js = "" # Fallback


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
        default=[]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("SoulStream detects your mood from your face or text and recommends music via Apple Music. Fully offline & powered by local ML.")

    # ─── Location / Language ───
    st.markdown("---")
    st.markdown("### 🌍 Music Region")
    st.caption("Select your region to get music in your local language.")
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

# ─── Header UI & Particle logic ─────────────────────────────
# This block handles both CSS and the particle background injection.
ui_html = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* Global Streamlit Overrides */
    .stApp {
        background: transparent !important;
        font-family: 'Outfit', sans-serif;
    }

    /* THEMED SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #0b0d1a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #f0f0f0 !important;
    }

    /* Fixed Particle Background Container */
    #tsparticles {
        position: fixed;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        z-index: -1;
        pointer-events: none;
        background: #050505;
        background-image: radial-gradient(circle at 50% 50%, #110e2d 0%, #050505 100%);
    }

    /* Content Layout */
    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
        position: relative;
        z-index: 1;
    }

    /* High Visibility Typography */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #e8e8e8 !important;
    }
    
    .hero-header {
        text-align: center;
        padding: 3rem 0 2rem 0;
    }

    .hero-header h1 {
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0px;
        letter-spacing: -3px;
        filter: drop-shadow(0 0 15px rgba(240, 147, 251, 0.3));
    }

    .hero-header p {
        color: #a8adc0 !important;
        font-size: 1.2rem;
        font-weight: 300;
        margin-top: 8px;
        letter-spacing: 1px;
    }

    /* Premium Glassmorphism Cards */
    .glass-card {
        background: rgba(20, 20, 35, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 28px;
        padding: 2.5rem;
        margin: 2rem 0;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.5);
    }

    /* Drag and Drop Pulse Effect */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed rgba(245, 87, 108, 0.3) !important;
        transition: all 0.3s ease-in-out !important;
        background: rgba(255, 255, 255, 0.02) !important;
    }
    
    [data-testid="stFileUploadDropzone"]:hover,
    [data-testid="stFileUploadDropzone"]:focus-within {
        border: 2px dashed #f5576c !important;
        background: rgba(245, 87, 108, 0.08) !important;
        transform: scale(1.01);
        animation: pulse-glow 2s infinite;
    }

    @keyframes pulse-glow {
        0% { box-shadow: 0 0 5px rgba(245, 87, 108, 0.2); }
        50% { box-shadow: 0 0 25px rgba(245, 87, 108, 0.5); }
        100% { box-shadow: 0 0 5px rgba(245, 87, 108, 0.2); }
    }

    /* Analysis Mode Radio Fix */
    div[role="radiogroup"] label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        margin-bottom: 8px !important;
        transition: 0.3s;
    }
    
    div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.08) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        color: #ffffff !important;
        padding: 0 28px;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(240, 147, 251, 0.2) 0%, rgba(245, 87, 108, 0.2) 100%) !important;
        border: 1px solid #f5576c !important;
        transform: translateY(-2px);
    }

    /* Inputs & Buttons */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: white !important;
        padding: 12px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        border: none !important;
        border-radius: 16px !important;
        color: white !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        height: 58px !important;
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.3);
        transition: 0.3s all;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 30px rgba(245, 87, 108, 0.5);
        color: white !important;
    }
</style>

<div id="tsparticles"></div>

<script>
    // CORE LIBRARY INSERTION
    LIBRARY_PLACEHOLDER
</script>

<script>
    // CONFIG & INITIALIZATION
    if (!window.tsParticlesStarted) {
        tsParticles.load("tsparticles", {
            "particles": {
                "number": { "value": 90, "density": { "enable": true, "area": 800 } },
                "color": { "value": ["#f093fb", "#f5576c"] },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.6, "random": true },
                "size": { "value": { "min": 1, "max": 4 }, "random": true },
                "links": { "enable": true, "distance": 150, "color": "#f093fb", "opacity": 0.35, "width": 1.5 },
                "move": { "enable": true, "speed": 1.8, "direction": "none", "random": true, "straight": false, "outModes": "out" }
            },
            "interactivity": {
                "detectsOn": "window",
                "events": { 
                    "onHover": { "enable": true, "mode": ["repulse", "grab"], "parallax": { "enable": true, "force": 60, "smooth": 15 } }, 
                    "resize": true 
                },
                "modes": { 
                    "repulse": { "distance": 180, "duration": 0.4 },
                    "grab": { "distance": 250, "links": { "opacity": 0.6 } }
                }
            },
            "retina_detect": true,
            "fpsLimit": 60
        });
        window.tsParticlesStarted = true;
    }
</script>
"""

st.markdown(ui_html.replace("LIBRARY_PLACEHOLDER", tsparticles_js or ""), unsafe_allow_html=True)

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
                    itunes_country = location_info.get("itunes_country", manual_itunes_country)

            result = None
            landmark_info = {"detected": False}

            if predict_source == "camera":
                if "Story Vibe" in analysis_mode:
                    from model.story_vibe import analyze_story_vibe
                    result = analyze_story_vibe(img_file)
                else:
                    result = analyze_face(img_file)

                try:
                    from model.landmark_detector import recognize_landmark
                    landmark_info = recognize_landmark(img_file)
                except Exception:
                    landmark_info = {"detected": False}
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
                reasoning = result.get("reasoning", "")

                # ── Emotion Result Card ──
                st.markdown(f"""
                <div class="emotion-result glass-card" style="border-right: 12px solid {color}; border-left: 12px solid {color}; text-align: center;">
                    <span style="font-size: 5rem; display: block;">{emoji}</span>
                    <h2 style="color: {color}; text-transform: uppercase; letter-spacing: 4px; margin: 1rem 0;">{emotion}</h2>
                    <p style="color: #a8adc0; font-style: italic; font-size: 1.1rem;">"{reasoning or 'Detected based on your input'}"</p>
                </div>
                """, unsafe_allow_html=True)

                # ── Location Intelligence Card ──
                if location_info.get("detected"):
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 1.5rem; border-left: 8px solid #f093fb;">
                        <h4 style="margin:0; color:#f093fb;">🌍 Location Detected</h4>
                        <p style="color:#ffffff; font-size:1.2rem; margin:0.5rem 0;"><b>{location_info.get('city', 'Unknown City')}, {location_info.get('country_code', '').upper()}</b></p>
                        <p style="color:#a8adc0; margin:0;">Mapping music results to the local storefront...</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Recommendations ──
                st.markdown("### 🎧 Soul-Matched Tracks")
                personal_context = f"{vibe_pref} {st.session_state.get('selected_genre', '')}".strip()
                
                recs = get_recommendations(
                    emotion,
                    keywords=keywords,
                    itunes_country=itunes_country,
                    favorite_artists=target_artists,
                    mentioned_artists=mentioned_artists,
                    genre=st.session_state.get('selected_genre'),
                    context_text=personal_context,
                    limit=10
                )

                if recs.get("songs"):
                    for song in recs["songs"]:
                        add_artist(song.get("artist", ""))
                        with st.container(border=False):
                            st.markdown(f"""
                            <div class="glass-card" style="margin: 0.5rem 0; padding: 1rem; background: rgba(255,255,255,0.02) !important;">
                                <div style="display: flex; align-items: center; gap: 20px;">
                                    <img src="{song.get('image')}" style="width: 80px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
                                    <div>
                                        <div style="font-weight: 800; font-size: 1.1rem; color:#fff;">{song['name']}</div>
                                        <div style="color: #f093fb; font-size: 0.9rem; margin-bottom: 8px;">{song['artist']}</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if song.get("preview"):
                                st.audio(song["preview"], format="audio/mp4")
                            
                            if song.get("url") and song["url"] != "#":
                                st.link_button(f"🎵 Open in Apple Music", song["url"], use_container_width=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.info("No network connection or songs found for this vibe. Try adjusting your preferences!")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("""
<div style="text-align: center; color: #4a4e60; font-size: 0.8rem; padding: 4rem 1rem 2rem 1rem;">
    SoulStream • Built with offline ML models & Apple Music API • v2.0
</div>
""", unsafe_allow_html=True)
