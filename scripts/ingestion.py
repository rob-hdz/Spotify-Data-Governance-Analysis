# Script for loading the raw Kaggle CVS / Spotify JSON into a pandas DataFrame
# Last update: 27/03/2026

import pandas as pd
import sqlite3
import os

##### CONSTANTS #####

# Paths
RAW_DATA_PATH = '../data/raw/spotify_data.csv'
DB_PATH = '../data/processed/spotify_vault.db'
SCHEMA_PATH = '../docs/schema.sql'

# Governance Lists
PII_COLUMNS = ['ip_address', 'user_email', 'user_account_id', 'gps_location', 'username']
MUSICAL_FEATURES = ['danceability_%', 'valence_%', 'energy_%', 'acousticness_%', 
                    'instrumentalness_%', 'liveness_%', 'speechiness_%']
VALID_KEYS = {'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'}
VALID_MODES = {'Major', 'Minor'}


##### DATA LOADING #####

def load_data(path):
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        return None
    
    try:
        data = pd.read_csv(path, encoding='latin-1') # Allows to read accents and special characters
        print("\nData loaded successfully!")
        print(f"Shape: {data.shape}") # Shows rows and columns
        return data
    except Exception as e: # Prevents crashing if an error occurs
        print(f"An error occurred: {e}")
        return None


##### DATA PRIVACY #####

def apply_privacy_filter(df): # Ensures data anonymization
    existing_pii = [col for col in PII_COLUMNS if col in df.columns]

    if existing_pii:
        df_clean = df.drop(columns = existing_pii)
        print(f"Privacy Filter: Dropped {len(existing_pii)} PII columns.")
        return df_clean
    else:
        print("Privacy Filter: No PII columns detected.")
        return df


##### DATA VALIDATION #####

def validate_data(df):
    initial_rows = len(df)

    # DQ-01: Drop if Name or Artist is missing
    df = df.dropna(subset=['track_name','artist(s)_name'])

    # DQ-02: Streams must be numeric and >= 0
    df['streams'] = pd.to_numeric(df['streams'], errors='coerce')
    df = df.loc[df['streams'] >= 0]

    # DQ-03: Musicality range [0, 100]
    for feature in MUSICAL_FEATURES:
        if feature in df.columns:
            df = df.loc[(df[feature] >= 0) & (df[feature] <= 100)]

    dropped_count = initial_rows - len(df)
    print(f"Validation: Rejected {dropped_count} rows. New shape: {df.shape}")
    return df

def transform_and_flag(df):
    # DQ-04: Transform playlist/chart counts to 0 if missing
    playlist_cols = [col for col in df.columns if 'playlists' in col or 'charts' in col]
    df[playlist_cols] = df[playlist_cols].fillna(0)

    # DQ-05: Artist count must be >= 1. Set it to None if it's 0 or negative
    df.loc[df['artist_count'] < 1, 'artist_count'] = None

    # DQ-06: Release date ranges
    df.loc[(df['released_year'] < 1900) | (df['released_year'] > 2026)] = None
    df.loc[(df['released_month'] < 1) | (df['released_month'] > 12)] = None
    df.loc[(df['released_day'] < 1) | (df['released_day'] > 31)] = None

    # DQ-07: Valid keys
    df.loc[~df['key'].isin(VALID_KEYS), 'key'] = None

    # DQ-08: Valid modes
    df.loc[~df['mode'].isin(VALID_MODES), 'mode'] = None

    # DQ-09: BPM Flagging [40, 250]
    df['quality_flag'] = 'Clean'
    bad_bpm = (df['bpm'] < 40) | (df['bpm'] > 250)
    df.loc[bad_bpm, 'quality_flag'] = 'Review BPM'

    flagged_count = len(df[df['quality_flag'] == 'Review BPM'])
    print(f"Transformation: Applied NULLs/0s. Flagged {flagged_count} rows for BPM review.")
    return df


##### TABLE CREATION #####

def initialize_database():
    # Connect or create the database file
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Read and execute schema.sql file
        with open(SCHEMA_PATH, 'r') as f:
            schema_script = f.read()

        cursor.executescript(schema_script)
        conn.commit() # Save changes

        print("Database: Connection estabished and Schema applied successfully.")
        return conn
    
    except Exception as e:
        print(f"Database Error: {e}")
        return None


##### LOADING #####

def load_to_sql(df, conn):
    try:
        df.to_sql(name='spotify_tracks', con=conn, if_exists='replace', index='False')
        print("Load: Data successfully written to spotify_vault.db")
    except Exception as e:
        print(f"Load Error: {e}")


##### QUALITY AUDIT #####

def generate_audit_report(initial_count, clean_df):
    final_count = len(clean_df)
    dropped_count = initial_count - final_count
    flagged_count = len(clean_df[clean_df['quality_flag'] == 'Review BPM'])

    print("\n" + "="*30)
    print("📊 DATA QUALITY AUDIT REPORT")
    print("="*30)
    print(f"Total Raw Rows Loaded:   {initial_count}")
    print(f"Rows Dropped (REJECT):   {dropped_count}")
    print(f"Rows Flagged (REVIEW):   {flagged_count}")
    print(f"Rows Saved to SQLite:    {final_count}")
    print(f"Data Health Score:       {(final_count/initial_count)*100:.1f}%")
    print("="*30 + "\n")

    # Save to text file
    with open('../docs/latest_audit.txt', 'w') as f:
        f.write(f"Audit Date: 2026-03\nSuccess: {final_count} tracks ingested.")


##### CHECK #####

def verify_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Count total rows
    cursor.execute("SELECT COUNT(*) FROM spotify_tracks")
    count = cursor.fetchone()[0]

    # Check for unexpected NULLs in critical columns
    cursor.execute("SELECT COUNT(*) FROM spotify_tracks WHERE track_name IS NULL")
    null_names = cursor.fetchone()[0]

    print(f"✅ Smoke Test: Found {count} rows in SQL.")
    if null_names == 0:
        print("✅ Quality Check: 0 NULL track names found. Data Integrity 100%.")
    else:
        print(f"⚠️  Warning: Found {null_names} NULL track names in SQL!")
    conn.close()


##### EXPORT #####

def export_for_powerbi():
    conn = sqlite3.connect(DB_PATH)
    # oNLY 'Clean' data for the dashboard
    df = pd.read_sql_query("SELECT * FROM spotify_tracks WHERE quality_flag = 'Clean'", conn)

    df.to_csv('../data/processed/spotify_gold_standard.csv', index=False)
    print("✅ Export: 'spotify_gold_standard.csv' created for Power BI! \n")
    conn.close()


##### MAIN BLOCK #####

if __name__ == "__main__": # Funtions can de borrowed without running the whole script
    
    # Extraction
    df_raw = load_data(RAW_DATA_PATH)
    if df_raw is not None:
        initial_count = len(df_raw)
        
        # Transformation
        df = apply_privacy_filter(df_raw)
        df = validate_data(df)
        df = transform_and_flag(df)
        
        # Loading
        conn = initialize_database()
        if conn:
            load_to_sql(df, conn)
            conn.close()
            
            # Auditing
            generate_audit_report(initial_count, df)

            # Check
            verify_database()

            # Export
            export_for_powerbi()
