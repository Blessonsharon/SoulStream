import os
import pandas as pd
from datasets import load_dataset

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_PATH = os.path.join(DATA_DIR, "huggingface_emotions.csv")

def download_and_prepare_dataset():
    """
    Downloads the industry-standard dair-ai/emotion dataset from HuggingFace.
    Maps fine-grained emotions down to our 4 core buckets.
    """
    print("Downloading dair-ai/emotion dataset from Hugging Face...")
    try:
        # Load the train split from the Hugging Face hub
        dataset = load_dataset("dair-ai/emotion", split="train")
        df = dataset.to_pandas()
        
        # dair-ai/emotion label mapping:
        # 0: sadness
        # 1: joy
        # 2: love
        # 3: anger
        # 4: fear
        # 5: surprise
        
        emotion_map = {
            0: "sad",
            1: "happy",
            2: "happy",     # map love down to happy
            3: "angry",
            4: "sad",       # fear can map to sad/melancholy music
            5: "neutral"    # surprise can map to neutral
        }
        
        df["mapped_emotion"] = df["label"].map(emotion_map)
        
        # Keep only necessary text and label
        df = df[["text", "mapped_emotion"]]
        df = df.rename(columns={"mapped_emotion": "label"})
        
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Save as CSV
        df.to_csv(CSV_PATH, index=False)
        print(f"Successfully downloaded and processed {len(df)} rows into {CSV_PATH}.")
        return CSV_PATH
    except Exception as e:
        print(f"Failed to fetch dataset: {e}")
        return None

if __name__ == "__main__":
    download_and_prepare_dataset()
