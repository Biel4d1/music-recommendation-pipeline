import os
import sqlite3
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors

# Path Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "music_data.db")

def find_similar_tracks(target_track_name: str, recommendation_count: int = 5):
    """
    Finds and recommends tracks from the local SQLite database that are
    geometrically closest to the targeted input song based on scaled audio properties.
    """
    if not os.path.exists(DB_FILE):
        print(f"CRITICAL ERROR: The database file '{DB_FILE}' does not exist. Run pipeline.py first.")
        return

    # 1. Load data into a Pandas DataFrame
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query("SELECT * FROM track_analytics", conn)

    if df.empty:
        print("WARNING: The track table is empty. Ingest data first.")
        return

    # Case-insensitive search for the target track name
    matched_tracks = df[df['track_name'].str.lower() == target_track_name.lower()]
    
    if matched_tracks.empty:
        print(f"\n❌ Track '{target_track_name}' not found in the database.")
        print("Available tracks to search for:")
        for name in df['track_name'].head(10):
            print(f" - {name}")
        return

    # Grab the first match
    seed_track = matched_tracks.iloc[0]
    seed_id = seed_track['track_id']

    print(f"\n🎯 TARGET TRACK IDENTIFIED:")
    print(f"   Name: '{seed_track['track_name']}' by {seed_track['artist_name']}")
    print(f"   Coordinates -> Valence: {seed_track['valence']:.4f} | Energy: {seed_track['energy']:.4f} | Tempo: {seed_track['tempo']:.2f} BPM")
    print(f"   Emotional Mood: {seed_track['calculated_emotion']}")
    print("-" * 70)

    # 2. Vector Normalization
    # Scale Tempo, Valence, and Energy to standard 0.0-1.0 limits so Euclidean distances are not distorted
    scaler = MinMaxScaler()
    features = ['valence', 'energy', 'tempo']
    
    df_scaled = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)
    df_scaled['track_id'] = df['track_id']

    # 3. Fit the Nearest Neighbors Model
    # We use metric='euclidean' to calculate the absolute straight-line distance in 3D vector space
    nn = NearestNeighbors(n_neighbors=recommendation_count + 1, metric='euclidean')
    nn.fit(df_scaled[features])

    # Extract coordinates for our seed track
    seed_index = df[df['track_id'] == seed_id].index[0]
    seed_vector = df_scaled.loc[[seed_index], features]

    # Calculate physical distances
    distances, indices = nn.kneighbors(seed_vector)

    # 4. Extract and print the recommendations
    print(f"RECOMMENDING TOP {recommendation_count} MATHEMATICAL MATCHES (Closest Vectors):")
    
    rank = 1
    for distance, idx in zip(distances[0], indices[0]):
        # Skip recommending the input track itself (distance will be exactly 0.0)
        if df.loc[idx, 'track_id'] == seed_id:
            continue
        
        recommended_track = df.loc[idx]
        print(f" {rank}. '{recommended_track['track_name']}' by {recommended_track['artist_name']}")
        print(f"    Mood: {recommended_track['calculated_emotion']}")
        print(f"    Geometric Distance: {distance:.4f}")
        print(f"    Valence: {recommended_track['valence']:.4f} | Energy: {recommended_track['energy']:.4f} | Tempo: {recommended_track['tempo']:.2f} BPM")
        print("-" * 50)
        
        rank += 1
        if rank > recommendation_count:
            break

if __name__ == "__main__":
    # Test with a known track in your database (Case-insensitive)
    find_similar_tracks("Night Changes", 5)
