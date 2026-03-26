-- This script creates the main table for the Spotify Data Governance and Analysis project
-- It follows the Governance rules defined in the Data Dictionary

CREATE TABLE IF NOT EXISTS spotify_tracks (
    
    row_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Generate a number (ID) for every song
    
    -- IDENTITY & METADATA
    track_name TEXT NOT NULL,
    artist_name TEXT NOT NULL,
    artist_count INTEGER,
    released_year INTEGER,
    released_month INTEGER,
    released_day INTEGER,

    -- METRICS
    streams BIGINT, -- BIGINT for numbers over 2 billion
    in_spotify_playlists INTEGER DEFAULT 0,
    in_spotify_charts INTEGER DEFAULT 0,

    -- MUSICALITY
    bpm FLOAT,
    key_note VARCHAR(5), -- I'll use Python later to check values
    mode_type VARCHAR(10), -- 'Major' or 'Minor'
    danceability_pct FLOAT CHECK (danceability_pct BETWEEN 0 AND 100),
    valence_pct FLOAT CHECK (valence_pct BETWEEN 0 AND 100),
    energy_pct FLOAT CHECK (energy_pct BETWEEN 0 AND 100),
    
    -- GOVERNANCE AUDIT COLUMNS 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(50) -- To track if it's Kaggle or personal Spotify
);

-- The `username` field from the raw JSON will be excluded from the SQL Schema to maintain user privacy (Anonymization).
