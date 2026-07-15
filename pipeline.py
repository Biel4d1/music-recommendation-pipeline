import os
import sqlite3
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "music_data.db")

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080")

def generate_deterministic_features(track_name: str, artist_name: str):
    """
    Generates deterministic but realistic audio features based on track names.
    This ensures that the same song always gets the same values, simulating real features.
    """
    # Seed the random generator with the song's name so it's consistent
    seed_str = f"{track_name}-{artist_name}"
    state = random.Random(seed_str)

    valence = state.uniform(0.1, 0.9)
    energy = state.uniform(0.1, 0.95)
    tempo = state.uniform(70.0, 180.0)
    mode = state.choice([0, 1])  # 0 for minor, 1 for major

    # Simple emotional heuristics
    if valence >= 0.5 and energy >= 0.5:
        emotion = "Euphoric / Upbeat"
    elif valence < 0.5 and energy >= 0.5:
        emotion = "Tense / Aggressive"
    elif valence < 0.5 and energy < 0.5:
        emotion = "Melancholic / Introspective"
    else:
        emotion = "Calm / Serene"

    return tempo, valence, energy, mode, emotion

def ingest_playlists(playlist_ids: list):
    print(f"Starting simulated ingestion for {len(playlist_ids)} playlist(s)...")

    if not CLIENT_ID or not CLIENT_SECRET:
        print("CRITICAL: Missing credentials. Run 'source .env' first.")
        return

    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="playlist-read-private"
        ))
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Spotify Client: {e}")
        return

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS track_analytics (
                    track_id TEXT PRIMARY KEY,
                    track_name TEXT,
                    artist_name TEXT,
                    tempo REAL,
                    valence REAL,
                    energy REAL,
                    mode INTEGER,
                    calculated_emotion TEXT
                );
            """)
            print("Database schema verified.")

            for p_id in playlist_ids:
                print(f"\nQuerying Spotify API for Track Metadata (Playlist: {p_id})...")
                results = sp.playlist_items(p_id)
                tracks = results.get("items", [])

                print(f"Retrieved raw item count: {len(tracks)}")

                success_count = 0
                skipped_count = 0

                for index, item in enumerate(tracks):
                    track = item.get("track") or item.get("item")
                    if not track:
                        continue

                    track_id = track.get("id")
                    track_name = track.get("name")
                    if not track_id:
                        continue

                    artists = track.get("artists", [])
                    artist_name = artists[0].get("name", "Unknown Artist") if artists else "Unknown Artist"

                    # Generate deterministic audio properties safely
                    tempo, valence, energy, mode, emotion = generate_deterministic_features(track_name, artist_name)

                    insert_query = """
                        INSERT OR IGNORE INTO track_analytics
                        (track_id, track_name, artist_name, tempo, valence, energy, mode, calculated_emotion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """

                    cursor = conn.cursor()
                    cursor.execute(insert_query, (
                        track_id, track_name, artist_name, tempo, valence, energy, mode, emotion
                    ))

                    if cursor.rowcount > 0:
                        print(f" SUCCESS [{success_count+1}]: '{track_name}' by {artist_name} -> Simulated Emotion: {emotion}")
                        success_count += 1
                    else:
                        skipped_count += 1

                print(f"Playlist Ingestion Summary: {success_count} loaded, {skipped_count} skipped/duplicates.")
                conn.commit()

            print("\nDatabase processing cycle complete.")

    except Exception as e:
        print(f"CRITICAL: Pipeline logic failed. Error Details: {e}")

if __name__ == "__main__":
    MY_PLAYLISTS = [
        "1YU6vA7OuaZ7y56j1qJRVn"
    ]
    ingest_playlists(MY_PLAYLISTS)
