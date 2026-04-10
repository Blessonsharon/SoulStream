import urllib.parse
import requests
from bs4 import BeautifulSoup
import random

def get_similar_artists(seed_artist: str, limit: int = 5) -> list:
    """
    Intelligently scrapes Last.fm's open association graph to find related artists.
    This bypasses expensive/locked ML APIs natively.
    """
    if not seed_artist:
        return []
        
    encoded_artist = urllib.parse.quote_plus(seed_artist)
    url = f"https://www.last.fm/music/{encoded_artist}/+similar"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Last.fm similar artists are enclosed in specific tags
        artist_elements = soup.select('.similar-artists-item-name')
        
        discovered = set()
        for elem in artist_elements:
            name = elem.get_text(strip=True)
            if name and name.lower() != seed_artist.lower():
                discovered.add(name)
                
        discovered_list = list(discovered)
        # Randomize the newly discovered batch to ensure infinite freshness 
        random.shuffle(discovered_list)
        
        return discovered_list[:limit]
        
    except Exception as e:
        print(f"Artist Discovery Graph failed: {e}")
        return []

# Test execution locally
if __name__ == "__main__":
    print(get_similar_artists("The Weeknd"))
