import os
import json
from mistralai.client import Mistral
from dotenv import load_dotenv

load_dotenv()

# Configure Mistral
api_key = os.getenv("MISTRAL_API_KEY")
client = None
if api_key:
    client = Mistral(api_key=api_key)

EMOTION_EMOJIS = {"happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐"}
EMOTION_COLORS = {"happy": "#FFD700", "sad": "#4A90D9", "angry": "#E74C3C", "neutral": "#95A5A6"}

def predict_emotion(text: str) -> dict:
    if not text or not text.strip():
        return {"emotion": None, "confidence": 0.0, "emoji": "❓", "color": "#666666", "all_scores": {}, "error": "Please enter text."}
    
    if not api_key or not client:
        return {"emotion": None, "confidence": 0.0, "emoji": "❓", "color": "#666666", "all_scores": {}, "error": "MISTRAL_API_KEY is missing from your .env file."}

    prompt = f"""
Analyze the following text and determine:
1. The primary emotion (EXACTLY one of: 'happy', 'sad', 'angry', 'neutral').
2. 2-3 specific "musical keywords" (e.g., "upbeat", "late night", "synth-pop").
3. A list of any "mentioned artists" (e.g., "The Weeknd", "Drake"). Extract them even if mentioned informally (e.g., "Weeknd").
4. A breakdown of scores for all four emotions.

Output ONLY valid JSON matching this schema:
{{
    "emotion": "sad",
    "musical_keywords": ["melancholy", "r&b", "lonely"],
    "mentioned_artists": ["The Weeknd"],
    "all_scores": {{
        "happy": 0.01,
        "sad": 0.95,
        "angry": 0.02,
        "neutral": 0.02
    }}
}}

Text to analyze: "{text}"
"""

    try:
        # Use Mistral chat completion with JSON mode
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse JSON output
        resp_text = response.choices[0].message.content.strip()
        data = json.loads(resp_text)
        
        predicted_emotion = data.get("emotion", "neutral").lower()
        musical_keywords = data.get("musical_keywords", [])
        mentioned_artists = data.get("mentioned_artists", [])
        all_scores = data.get("all_scores", {"happy": 0.25, "sad": 0.25, "angry": 0.25, "neutral": 0.25})
        
        # Fallback for hallucinated emotions
        if predicted_emotion not in EMOTION_EMOJIS:
            predicted_emotion = "neutral"
            
        confidence = float(all_scores.get(predicted_emotion, 0.5))

        return {
            "emotion": predicted_emotion,
            "musical_keywords": musical_keywords,
            "mentioned_artists": mentioned_artists,
            "confidence": confidence,
            "emoji": EMOTION_EMOJIS.get(predicted_emotion, "🤔"),
            "color": EMOTION_COLORS.get(predicted_emotion, "#666666"),
            "all_scores": all_scores,
        }
    except Exception as e:
        return {"emotion": None, "confidence": 0.0, "emoji": "❓", "color": "#666666", "all_scores": {}, "error": f"Mistral API Error: {str(e)}"}
