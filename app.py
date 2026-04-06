"""
🎵 Mood-Based Music Recommender
Streamlit application — detects emotion from text and recommends Spotify songs.
"""

import streamlit as st
import sys
import os

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
            current_text = st.session_state.get('user_text_input', '')
            st.session_state.user_text_input = f"{current_text} {selected}".strip()
            st.rerun()

@st.dialog("Select Genre")
def show_genre_dialog():
    selected = st.selectbox("Music Genres", DEFAULT_GENRES)
    if st.button("Add"):
        st.session_state.selected_genre = selected
        current_text = st.session_state.get('user_text_input', '')
        st.session_state.user_text_input = f"{current_text} {selected}".strip()
        st.rerun()

# ─── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Mood Music Recommender",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── Sidebar Settings ──────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    simplified_ui = st.toggle("Simplified UI", value=True, help="Hide technical details like confidence scores and emotion breakdowns.")
    open_top_pick = st.toggle("Show 'Open Top Pick' Button", value=True, help="Display a prominent button for the top recommended song.")
    player_mode = st.radio("Player Style", ["Embedded Player", "Compact List"], index=0, help="Choose how you want to listen to recommendations.")
    
    st.markdown("---")
    st.markdown("### 🧬 Training & Personalization")
    target_artists = st.multiselect(
        "Focus on these artists:",
        ["The Weeknd", "Drake", "Taylor Swift", "Billie Eilish", "Dua Lipa", "Travis Scott", "Eminem", "Kendrick Lamar", "Adele"],
        default=["The Weeknd"],
        help="Select your favorite artists to focus the recommendations around their discography."
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("Detect your mood from text and get personalized Spotify recommendations.")

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
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global Styles ── */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1333 40%, #24243e 100%);
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }

    /* ── Header ── */
    .hero-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .hero-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }

    .hero-header p {
        color: #8b8fa3;
        font-size: 1.05rem;
        font-weight: 300;
        margin-top: 0;
    }

    /* ── Glass Card ── */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1rem 0;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }

    /* ── Emotion Result ── */
    .emotion-result {
        text-align: center;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 16px;
        animation: fadeInUp 0.5s ease-out;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .emotion-emoji {
        font-size: 4rem;
        display: block;
        margin-bottom: 0.5rem;
    }

    .emotion-label {
        font-size: 1.6rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0.3rem 0;
    }

    .confidence-text {
        font-size: 1rem;
        color: #a8adc0;
        font-weight: 400;
    }

    /* ── Song Card ── */
    .song-card {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.7rem;
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
    }

    .song-card:hover {
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateX(4px);
    }

    .song-img {
        width: 56px;
        height: 56px;
        border-radius: 8px;
        object-fit: cover;
        flex-shrink: 0;
    }

    .song-img-placeholder {
        width: 56px;
        height: 56px;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }

    .song-info {
        flex-grow: 1;
        min-width: 0;
    }

    .song-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e8e8f0;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .song-artist {
        font-size: 0.82rem;
        color: #8b8fa3;
        margin: 0.15rem 0 0 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .song-album {
        font-size: 0.75rem;
        color: #5a5e70;
        margin: 0.1rem 0 0 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .song-link {
        flex-shrink: 0;
    }

    .song-link a {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: linear-gradient(135deg, #1DB954, #1ed760);
        color: white !important;
        text-decoration: none;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .song-link a:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(30, 215, 96, 0.3);
    }

    /* ── Score Bars ── */
    .score-bar-container {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 0.35rem 0;
    }

    .score-bar-label {
        width: 70px;
        font-size: 0.8rem;
        color: #8b8fa3;
        text-align: right;
        font-weight: 500;
    }

    .score-bar-track {
        flex-grow: 1;
        height: 8px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 4px;
        overflow: hidden;
    }

    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.8s ease;
    }

    .score-bar-value {
        width: 48px;
        font-size: 0.8rem;
        color: #a8adc0;
        font-weight: 500;
    }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1.5rem 0 0.8rem 0;
    }

    .section-header h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #c8cad8;
        margin: 0;
    }

    /* ── Source Badge ── */
    .source-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.25rem 0.7rem;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .source-spotify {
        background: rgba(30, 215, 96, 0.1);
        color: #1DB954;
        border: 1px solid rgba(30, 215, 96, 0.2);
    }

    .source-fallback {
        background: rgba(255, 193, 7, 0.1);
        color: #FFC107;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }

    /* ── Divider ── */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 1.5rem 0;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        color: #4a4e60;
        font-size: 0.78rem;
        padding: 2rem 0 1rem 0;
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Text area styling ── */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e8e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 1rem !important;
    }

    .stTextArea textarea:focus {
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.15) !important;
    }

    .stTextArea textarea::placeholder {
        color: #5a5e70 !important;
    }

    /* ── Button ── */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.65rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Alert styling ── */
    .stAlert {
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🎵 Mood Music</h1>
    <p>Detect your emotion from text • Get personalized song recommendations</p>
</div>
""", unsafe_allow_html=True)


# ─── Input Section ─────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

user_text = st.text_area(
    "How are you feeling?",
    placeholder="Type how you're feeling right now... e.g., 'I'm so excited about my promotion today!'",
    height=120,
    label_visibility="collapsed",
    key="user_text_input"
)

# Sync session_state user_text for dialogs
st.session_state.user_text = st.session_state.get('user_text_input', '')

analyze_clicked = st.button("🔍  Detect Mood & Recommend Songs", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# ─── Results ───────────────────────────────────────────────
if analyze_clicked:
    if not user_text or not user_text.strip():
        st.warning("⚠️ Please enter some text to analyze your mood.")
    else:
        # Import modules
        with st.spinner("🧠 Analyzing your mood..."):
            try:
                from model.predict import predict_emotion
                from spotify.recommender import get_recommendations

                # Predict emotion
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

                    # ── Emotion Result Card ──
                    confidence_html = f'<div class="confidence-text">Confidence: {confidence:.1%}</div>' if not simplified_ui else ""
                    keyword_badges = " ".join([f'<span style="background: {color}20; color: {color}; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; margin-right: 4px;">#{k}</span>' for k in keywords]) if keywords else ""
                    artist_badge = f'<div style="margin-top: 8px; font-size: 0.85rem; color: #8b8fa3;">🎙️ Artist Detected: <b style="color: white;">{", ".join(mentioned_artists)}</b></div>' if mentioned_artists else ""
                    
                    st.markdown(f"""
                    <div class="emotion-result glass-card" style="border-color: {color}40;">
                        <span class="emotion-emoji">{emoji}</span>
                        <div class="emotion-label" style="color: {color};">{emotion}</div>
                        <div style="margin-bottom: 8px;">{keyword_badges}</div>
                        {artist_badge}
                        {confidence_html}
                    </div>
                    """, unsafe_allow_html=True)

                # ── Score Breakdown ──
                if not simplified_ui:
                    st.markdown("""
                    <div class="section-header">
                        <h3>📊 Emotion Breakdown</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    score_colors = {
                        "happy": "#FFD700",
                        "sad": "#4A90D9",
                        "angry": "#E74C3C",
                        "neutral": "#95A5A6",
                    }

                    bars_html = ""
                    for emo, score in sorted(all_scores.items(), key=lambda x: -x[1]):
                        bar_color = score_colors.get(emo, "#667eea")
                        width_pct = score * 100
                        bars_html += f"""
                        <div class="score-bar-container">
                            <span class="score-bar-label">{emo.capitalize()}</span>
                            <div class="score-bar-track">
                                <div class="score-bar-fill" style="width: {width_pct}%; background: {bar_color};"></div>
                            </div>
                            <span class="score-bar-value">{score:.1%}</span>
                        </div>
                        """

                    st.markdown(f'<div class="glass-card">{bars_html}</div>', unsafe_allow_html=True)

                    # ── Divider ──
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

                # ── Song Recommendations ──
                st.markdown("""
                <div class="section-header">
                    <h3>🎧 Recommended Songs</h3>
                </div>
                """, unsafe_allow_html=True)

                recs = get_recommendations(
    emotion,
    keywords=keywords,
    favorite_artists=target_artists,
    mentioned_artists=mentioned_artists,
    genre=st.session_state.get('selected_genre'),
    limit=10
)
                source = recs["source"]
                query = recs["query"]

                # Source badge
                if source == "spotify":
                    st.markdown(f"""
                    <span class="source-badge source-spotify">
                        🟢 Powered by Spotify
                    </span>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <span class="source-badge source-fallback">
                        ⚠️ Curated picks (Spotify API not connected)
                    </span>
                    """, unsafe_allow_html=True)

                # ── Top Pick Button ──
                if open_top_pick and recs.get("songs"):
                    top_song = recs["songs"][0]
                    if top_song["url"] != "#":
                        st.link_button(f"🎵 Open Top Pick: {top_song['name']} on Spotify", top_song["url"], use_container_width=True)
                        st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

                # Song results
                for song in recs["songs"]:
                    # Persist artist to discovery history
                    add_artist(song.get("artist", ""))
                    if player_mode == "Embedded Player" and song.get("id"):
                        # Spotify Embed Player
                        embed_url = f"https://open.spotify.com/embed/track/{song['id']}?utm_source=generator&theme=0"
                        st.components.v1.iframe(embed_url, height=80, scrolling=False)
                    else:
                        # Compact List Mode (Native Streamlit)
                        with st.container():
                            col1, col2, col3 = st.columns([1, 3, 1.2], vertical_alignment="center")
                            
                            with col1:
                                if song.get("image"):
                                    st.image(song["image"], use_container_width=True)
                                else:
                                    st.markdown('<div class="song-img-placeholder" style="width: 100%; aspect-ratio: 1/1;">🎵</div>', unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"**{song['name']}**")
                                st.markdown(f"<p style='color: #8b8fa3; font-size: 0.82rem; margin-top: -10px;'>{song['artist']}<br>{song.get('album', '')}</p>", unsafe_allow_html=True)
                            
                            with col3:
                                if song["url"] != "#":
                                    st.link_button("▶ Play", song["url"], use_container_width=True)
                            
                            st.markdown('<div style="margin-bottom: 0.3rem;"></div>', unsafe_allow_html=True)

                # ── Feedback Loop ──
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown('<div style="text-align: center; color: #8b8fa3; font-size: 0.85rem;">Did we get the mood right?</div>', unsafe_allow_html=True)
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    if st.button("👍 Correct!", use_container_width=True):
                        st.toast("Thanks! We're learning... ✨")
                with f_col2:
                    if st.button("👎 Not quite", use_container_width=True):
                        st.toast("We'll try harder next time! 🧠")

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("""
<div class="footer">
    Built with TensorFlow · Spotify API · Streamlit<br>
    Mood-Based Music Recommender — Deep Learning Mini Project
</div>
""", unsafe_allow_html=True)
