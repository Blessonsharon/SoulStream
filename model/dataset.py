DATASET = [
    # Happy
    ("I'm feeling so happy and energetic today!", "happy"),
    ("What a wonderful day, the sun is shining.", "happy"),
    ("I passed my exam! I'm on top of the world.", "happy"),
    ("Such good news, I'm thrilled.", "happy"),
    ("Feeling great, let's dance!", "happy"),
    ("I love everything right now.", "happy"),
    ("Best day of my life, totally ecstatic.", "happy"),
    ("Smiling from ear to ear.", "happy"),
    
    # Sad
    ("I'm feeling really sad and down.", "sad"),
    ("Nothing is going right, I feel miserable.", "sad"),
    ("I just want to cry in bed all day.", "sad"),
    ("So heartbroken and lonely.", "sad"),
    ("Feeling melancholy and blue.", "sad"),
    ("I miss them so much.", "sad"),
    ("Everything is so depressing.", "sad"),
    ("Tears are falling, I'm so unhappy.", "sad"),
    
    # Angry
    ("I am so furious right now, don't talk to me.", "angry"),
    ("This is completely unacceptable and maddening!", "angry"),
    ("I hate how people treat me sometimes.", "angry"),
    ("Punch a wall, I'm raging.", "angry"),
    ("So mad I could scream.", "angry"),
    ("This makes my blood boil.", "angry"),
    ("Frustrated beyond belief.", "angry"),
    ("I'm annoyed and irritated.", "angry"),
    
    # Neutral
    ("I'm just chilling, nothing much.", "neutral"),
    ("Going for my usual walk.", "neutral"),
    ("Just ate a sandwich, it was okay.", "neutral"),
    ("Reading a book in the evening.", "neutral"),
    ("Doing some laundry right now.", "neutral"),
    ("Sitting and waiting for the bus.", "neutral"),
    ("Feeling alright, a bit indifferent.", "neutral"),
    ("Just a normal day.", "neutral"),
]

MUSICAL_KEYWORDS_MAP = {
    "happy":         ["upbeat", "energetic", "pop", "dance", "cheerful"],
    "sad":           ["melancholy", "acoustic", "slow", "r&b", "lonely"],
    "angry":         ["intense", "heavy", "rock", "metal", "fast"],
    "neutral":       ["lofi", "chill", "ambient", "indie", "relaxing"],
    "party":         ["edm", "dance", "club", "house", "upbeat", "electronic"],
    "lust":          ["rnb", "slow jam", "sensual", "neo soul", "smooth"],
    "hangover":      ["chill", "acoustic", "soft", "folk", "quiet"],
    "breakup":       ["heartbreak", "ballad", "sad acoustic", "soul", "indie"],
    "depression":    ["dark", "slow", "minimal", "ambient", "melancholy"],
    "lonely":        ["acoustic", "folk", "indie", "quiet", "reflective"],
    "stressed":      ["alternative", "rock", "intense", "heavy", "noise"],
    "anxiety":       ["electronic", "dark", "moody", "tense", "alternative"],
    "adrenaline rush":["hype", "heavy", "bass", "metal", "hardcore"],
    "gym":           ["workout", "trap", "hip hop", "heavy", "hype"],
    "athletic":      ["motivational", "rock", "energetic", "upbeat", "sport"],
    "love":          ["romantic", "soul", "pop", "ballad", "warm"],
    "aesthetic":     ["dream pop", "lo-fi", "indie", "chill", "shoegaze"],
}

KNOWN_ARTISTS = [
    "The Weeknd", "Drake", "Taylor Swift", "Billie Eilish", 
    "Dua Lipa", "Travis Scott", "Eminem", "Kendrick Lamar", 
    "Adele", "Ariana Grande", "Post Malone", "Ed Sheeran"
]
