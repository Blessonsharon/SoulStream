import os
from dotenv import load_dotenv

load_dotenv()

EMOTION_QUERIES = {
    "happy": "happy upbeat top hits The Weeknd Dua Lipa",
    "sad": "sad moody top hits The Weeknd Billie Eilish",
    "angry": "high energy workout top hits Travis Scott Eminem",
    "neutral": "chill lofi top hits The Weeknd Taylor Swift",
}

FALLBACK_SONGS = {
    "happy": [
        {"name": "Blinding Lights", "artist": "The Weeknd", "album": "After Hours", "url": "https://open.spotify.com/track/0VjIj9n21oL6G9YFmbuvLc", "id": "0VjIj9n21oL6G9YFmbuvLc", "image": "https://i.scdn.co/image/ab67616d0000b273886574a682da0d7af72e987c"},
        {"name": "Levitating", "artist": "Dua Lipa", "album": "Future Nostalgia", "url": "https://open.spotify.com/track/39Yp9vG1oYpBveqc9oIyEO", "id": "39Yp9vG1oYpBveqc9oIyEO", "image": "https://i.scdn.co/image/ab67616d0000b273bd339908ef946487e4760a92"},
        {"name": "Shake It Off", "artist": "Taylor Swift", "album": "1989", "url": "https://open.spotify.com/track/079hfY19tELp8Bu7p99999", "id": "079hfY19tELp8Bu7p99999", "image": "https://i.scdn.co/image/ab67616d0000b2733592cf7d7274530fc4938634"},
    ],
    "sad": [
        {"name": "Save Your Tears", "artist": "The Weeknd", "album": "After Hours", "url": "https://open.spotify.com/track/5Y9m9vB1oYpBveqc9oIyEO", "id": "5Y9m9vB1oYpBveqc9oIyEO", "image": "https://i.scdn.co/image/ab67616d0000b273886574a682da0d7af72e987c"},
        {"name": "Anti-Hero", "artist": "Taylor Swift", "album": "Midnights", "url": "https://open.spotify.com/track/0V3MvB1oYpBveqc9oIyEO", "id": "0V3MvB1oYpBveqc9oIyEO", "image": "https://i.scdn.co/image/ab67616d0000b273bbade30e70b3726581b29a28"},
        {"name": "Someone Like You", "artist": "Adele", "album": "21", "url": "https://open.spotify.com/track/4Y9m9vB1oYpBveqc9oIyEO", "id": "4Y9m9vB1oYpBveqc9oIyEO", "image": "https://i.scdn.co/image/ab67616d0000b2732115aad591662479f64cd512"},
    ],
    "angry": [
        {"name": "SICKO MODE", "artist": "Travis Scott", "album": "ASTROWORLD", "url": "https://open.spotify.com/track/0V0MvB1oYpBveqc9oIyEO", "id": "2xmqye6gAegTMjLKEBoR3d", "image": "https://i.scdn.co/image/ab67616d0000b27307220556284d7f57be2c9aba"},
        {"name": "Godzilla", "artist": "Eminem", "album": "Music To Be Murdered By", "url": "https://open.spotify.com/track/7Y9m9vB1oYpBveqc9oIyEO", "id": "7Y9m9vB1oYpBveqc9oIyEO", "image": "https://i.scdn.co/image/ab67616d0000b27387cc8e79b90c108a73562479"},
        {"name": "Humble", "artist": "Kendrick Lamar", "album": "DAMN.", "url": "https://open.spotify.com/track/0VmMvB1oYpBveqc9oIyEO", "id": "0VmMvB1oYpBveqc9oIyEO", "image": "https://i.scdn.co/image/ab67616d0000b27318ec85b46b863073747ebc79"},
    ],
    "neutral": [
        {"name": "Starboy", "artist": "The Weeknd", "album": "Starboy", "url": "https://open.spotify.com/track/0VvMvB1oYpBveqc9oIyEO", "id": "0VvMvB1oYpBveqc9oIyEO", "image": "https://i.scdn.co/image/ab67616d0000b2734718e2b124f0563457ed7026"},
        {"name": "Cruel Summer", "artist": "Taylor Swift", "album": "Lover", "url": "https://open.spotify.com/track/0VWMvB1oYpBveqc9oIyEO", "id": "1BxfuLs2zO6tSefXoVYLEL", "image": "https://i.scdn.co/image/ab67616d0000b273e787cffec20aa2a0962daa2b"},
        {"name": "Passionfruit", "artist": "Drake", "album": "More Life", "url": "https://open.spotify.com/track/0VXMvB1oYpBveqc9oIyEO", "id": "5mY9m9vB1oYpBveqc9oIyEO", "image": "https://i.scdn.co/image/ab67616d0000b27394a2f5a40147982daa2b"},
    ],
}

def _get_spotify_client():
    client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    if not client_id or not client_secret or client_id == "your_client_id_here":
        return None
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        sp.search(q="test", type="track", limit=1)
        return sp
    except:
        return None

def get_recommendations(emotion: str, keywords: list = None, favorite_artists: list = None, mentioned_artists: list = None, genre: str = None, context_text: str = "", limit: int = 10) -> dict:
    # ── Build Search Query ──
    # Priority: Mentioned Artists > Favorite Artists
    priority_artists = mentioned_artists if mentioned_artists else favorite_artists
    
    # Add keywords from AI
    keyword_str = " ".join(keywords) if keywords else ""
    
    # Priority Artists
    artist_query = ""
    if priority_artists:
        # Format as artist:"Name" artist:"Name"
        artist_query = " ".join([f'artist:"{a}"' for a in priority_artists])
    
    # Genre query
    genre_query = f'genre:"{genre}"' if genre else ""

    # Combine everything
    # Example: artist:"The Weeknd" artist:"Drake" genre:"Pop" late night melancholy sad
    final_query = f"{artist_query} {genre_query} {keyword_str} {context_text} {emotion}".strip()
    
    # Fallback if final query is empty (unlikely)
    if not final_query:
        final_query = EMOTION_QUERIES.get(emotion, "chill relaxing")

    sp = _get_spotify_client()
    if sp:
        try:
            results = sp.search(q=final_query, type="track", limit=limit)
            tracks = results.get("tracks", {}).get("items", [])
            
            # Logic for prioritizing artist
            if not tracks and mentioned_artists:
                # Retry 1: Prioritize the artist if combined search failed
                # (Maybe the artist doesn't have a song that perfectly matches the "mood" word)
                retry_query = artist_query.strip()
                results = sp.search(q=retry_query, type="track", limit=limit)
                tracks = results.get("tracks", {}).get("items", [])
                if tracks:
                    final_query = retry_query

            if not tracks and not mentioned_artists and favorite_artists:
                # Retry for favorites if too restrictive
                retry_query = f"{keyword_str} {emotion}".strip()
                results = sp.search(q=retry_query, type="track", limit=limit)
                tracks = results.get("tracks", {}).get("items", [])
                if tracks:
                    final_query = retry_query

            # Final Fallback: If still nothing, try a very broad mood search
            if not tracks:
                retry_query = EMOTION_QUERIES.get(emotion, "top hits")
                results = sp.search(q=retry_query, type="track", limit=limit)
                tracks = results.get("tracks", {}).get("items", [])
                if tracks:
                    final_query = retry_query

            songs = []
            for track in tracks:
                images = track.get("album", {}).get("images", [])
                image_url = images[0]["url"] if images else None
                songs.append({
                    "name": track["name"],
                    "artist": ", ".join(a["name"] for a in track["artists"]),
                    "album": track.get("album", {}).get("name", "Unknown"),
                    "url": track["external_urls"].get("spotify", "#"),
                    "id": track["id"],
                    "image": image_url,
                })
            
            if songs:
                return {"songs": songs, "source": "spotify", "query": final_query}
        except:
            pass
            
    # Fallback to curated picks if Spotify fails or returns nothing
    fallback = FALLBACK_SONGS.get(emotion, FALLBACK_SONGS["neutral"])
    return {"songs": fallback[:limit], "source": "fallback", "query": final_query}
