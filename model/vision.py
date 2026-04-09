import os
import json
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

EMOTION_EMOJIS = {"happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐"}
EMOTION_COLORS = {"happy": "#FFD700", "sad": "#4A90D9", "angry": "#E74C3C", "neutral": "#95A5A6"}

def analyze_face(image_input) -> dict:
    """
    Analyzes a facial expression from an image using Gemini 1.5 Flash.
    image_input can be a PIL Image or bytes.
    """
    if not api_key:
        return {"error": "GEMINI_API_KEY is missing from your .env file."}

    try:
        # Load the model
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Prepare the image
        if not isinstance(image_input, Image.Image):
            img = Image.open(image_input)
        else:
            img = image_input

        prompt = """
        Analyze the facial expression of the person in this image and determine:
        1. The primary emotion (EXACTLY one of: 'happy', 'sad', 'angry', 'neutral').
        2. 2-3 specific "musical keywords" based on their expression (e.g., "upbeat", "late night", "melancholy").
        3. A breakdown of scores (probabilities) for all four emotions.

        Output ONLY valid JSON matching this schema:
        {
            "emotion": "happy",
            "musical_keywords": ["upbeat", "energetic"],
            "all_scores": {
                "happy": 0.9,
                "sad": 0.02,
                "angry": 0.03,
                "neutral": 0.05
            },
            "reasoning": "Brief explanation of why this emotion was chosen."
        }
        """

        response = model.generate_content([prompt, img])
        
        # Parse JSON output
        # Handle cases where the model might wrap JSON in backticks
        resp_text = response.text.strip()
        if resp_text.startswith("```json"):
            resp_text = resp_text.replace("```json", "", 1).replace("```", "", 1).strip()
        elif resp_text.startswith("```"):
            resp_text = resp_text.replace("```", "", 1).replace("```", "", 1).strip()
            
        data = json.loads(resp_text)
        
        predicted_emotion = data.get("emotion", "neutral").lower()
        if predicted_emotion not in EMOTION_EMOJIS:
            predicted_emotion = "neutral"
            
        all_scores = data.get("all_scores", {"happy": 0.25, "sad": 0.25, "angry": 0.25, "neutral": 0.25})
        confidence = float(all_scores.get(predicted_emotion, 0.5))

        return {
            "emotion": predicted_emotion,
            "musical_keywords": data.get("musical_keywords", []),
            "confidence": confidence,
            "emoji": EMOTION_EMOJIS.get(predicted_emotion, "🤔"),
            "color": EMOTION_COLORS.get(predicted_emotion, "#666666"),
            "all_scores": all_scores,
            "reasoning": data.get("reasoning", "")
        }

    except Exception as e:
        return {"error": f"Gemini Vision Error: {str(e)}"}
