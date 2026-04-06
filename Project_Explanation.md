# Mood-Based Music Recommender - Project Explanation

## Overview
This project is an end-to-end AI application that predicts a user's emotion from the text they enter and recommends music via Spotify that perfectly aligns with that emotion.

## Core Components
### 1. Generative AI Inference (`model/predict.py`)
- We have fully replaced the legacy Deep Learning models and dataset pipelines with a smart Large Language Model architecture.
- When an end-user provides text, we pass it into the **Google Gemini Pro API** (`gemini-1.5-pro`).
- A precise prompt specifically tells Gemini to act as a structured classification algorithm. We enforce a response format to output strict JSON mapping to the four emotion buckets (`happy`, `sad`, `angry`, `neutral`) along with dynamic confidence scores for each state. 

### 2. Spotify Integration (`spotify/recommender.py`)
- Based on the emotion determined by Gemini, a corresponding search query is formed (e.g., "sad" mapped to "sad slow", "happy" mapped to "happy upbeat").
- It uses the Spotipy library coupled with the Spotify API to search for relevant tracks.
- In case API credentials are unset or invalid, it gracefully falls back to an offline dictionary mapping predefined tracks to each emotion class.

### 3. Web Interface (`app.py`)
- Created using Streamlit, providing an interactive, user-friendly frontend.
- Contains custom CSS with glassmorphism to look modern and refined.
- Decodes the JSON received from the Gemini API and provides visual breakdowns of AI confidence across the different emotional states using bars.
