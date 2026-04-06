import os
from model.predict import predict_emotion
from spotify.recommender import get_recommendations

def test_recommendation(text):
    print(f"\n--- Testing: '{text}' ---")
    result = predict_emotion(text)
    emotion = result["emotion"]
    keywords = result.get("musical_keywords", [])
    mentioned_artists = result.get("mentioned_artists", [])
    
    print(f"Detected Emotion: {emotion}")
    print(f"Keywords: {keywords}")
    print(f"Mentioned Artists: {mentioned_artists}")
    
    recs = get_recommendations(emotion, keywords=keywords, favorite_artists=["The Weeknd"], mentioned_artists=mentioned_artists)
    
    print(f"Search Query: {recs.get('query')}")
    print(f"Source: {recs.get('source')}")
    for i, song in enumerate(recs.get("songs", []), 1):
        print(f"{i}. {song['name']} - {song['artist']}")

if __name__ == "__main__":
    # Case 1: Mentioned artist (The Weeknd) + Mood (Sad)
    test_recommendation("I'm feeling really sad, play some The Weeknd")
    
    # Case 2: Mentioned artist (Taylor Swift) + Mood (Happy)
    test_recommendation("I'm so happy today! Play Taylor Swift.")
    
    # Case 3: No artist mentioned (should use favorites or mood)
    test_recommendation("I'm feeling angry and energetic!")
