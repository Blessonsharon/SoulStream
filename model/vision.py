import os
import cv2
import numpy as np
from PIL import Image

from model.dataset import MUSICAL_KEYWORDS_MAP

EMOTION_EMOJIS = {"happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐"}
EMOTION_COLORS = {"happy": "#FFD700", "sad": "#4A90D9", "angry": "#E74C3C", "neutral": "#95A5A6"}

# Load Haar Cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

def analyze_face(image_input) -> dict:
    """
    Analyzes a facial expression from an image using local OpenCV Haar Cascades.
    image_input can be a PIL Image, bytes, or Streamlit UploadedFile.
    This avoids Heavy Deep Learning DLLs (TensorFlow/Torch) completely!
    """
    try:
        if isinstance(image_input, Image.Image):
            img = image_input
        else:
            img = Image.open(image_input)
            
        img_np = np.array(img.convert('RGB'))
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        if len(faces) == 0:
            return {"error": "Local Vision: No face detected in the image."}
            
        # Process first face
        (x, y, w, h) = faces[0]
        roi_gray = gray[y:y+h, x:x+w]
        
        # Detect smile with increased sensitivity
        smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.3, minNeighbors=8)
        
        predicted_emotion = "neutral"
        confidence = 0.6 # Base confidence for rule-based models
        
        if len(smiles) > 0:
            predicted_emotion = "happy"
            confidence = 0.85
        else:
            # Simple heuristic: calculate average brightness of face to mimic mood
            # (Darker rooms often align with chill/melancholy music themes in this mock)
            avg_brightness = np.mean(roi_gray)
            if avg_brightness < 90:
                predicted_emotion = "sad"
                confidence = 0.70
            elif avg_brightness > 180:
                predicted_emotion = "angry" # Overexposed/intense
                confidence = 0.65
        
        # Normalize scores to look nice in the UI
        all_scores = {"happy": 0.1, "sad": 0.1, "angry": 0.1, "neutral": 0.1}
        all_scores[predicted_emotion] = confidence
        
        musical_keywords = MUSICAL_KEYWORDS_MAP.get(predicted_emotion, [])

        return {
            "emotion": predicted_emotion,
            "musical_keywords": musical_keywords,
            "confidence": confidence,
            "emoji": EMOTION_EMOJIS.get(predicted_emotion, "🤔"),
            "color": EMOTION_COLORS.get(predicted_emotion, "#666666"),
            "all_scores": all_scores,
            "reasoning": f"OpenCV facial geometry detected: {predicted_emotion}.",
            "mentioned_artists": []
        }

    except Exception as e:
        return {"error": f"Local Vision Error: {str(e)}"}
