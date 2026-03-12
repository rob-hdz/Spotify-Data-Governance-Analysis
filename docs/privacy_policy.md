# Privacy Policy

Since I intend to use my personal Spotify account data, I have the responsibility to protect my own identity. Therefore, three privacy levels are state as follows:

**Level 1 (Public):** Track name, artist(s), release date, metrics. (Safe to upload to GitHub)

**Level 2 (Internal):** Playback timestamps. (I consent to share this information)

**Level 3 (Restricted):** IP address, user email, user account ID, GPS location. (I do not consent to share this information)

&ensp;

*During the Ingestion phase (Python), all Level 3 fields will be dropped using the `.drop()` method in pandas before the data is saved to the SQLite database. 
No Personal Identifiable Information (PII) will ever reach the `processed/` data folder or the public GitHub repository.*
