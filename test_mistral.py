import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from model.predict import predict_emotion
    
    test_text = "I am so happy today, everything is going great!"
    print(f"Testing with text: '{test_text}'")
    
    result = predict_emotion(test_text)
    
    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        print(f"Emotion: {result['emotion']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Emoji: {result['emoji']}")
        print(f"All Scores: {result['all_scores']}")
        
except Exception as e:
    print(f"An exception occurred: {str(e)}")
