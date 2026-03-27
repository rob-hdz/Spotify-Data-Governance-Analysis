-- DATA ANALYSIS QUERIES

-- Top 10 Artists by Total Streams
SELECT
    "artist(s)_name",
    COUNT(track_name) AS total_tracks,
    SUM(streams) AS total_streams,
    ROUND(AVG("danceability_%"), 2) AS avg_danceability
FROM spotify_tracks
WHERE "artist(s)_name" IS NOT NULL
GROUP BY "artist(s)_name"
ORDER BY total_streams DESC
LIMIT 10;

-- Check Governance flags
SELECT
    quality_flag,
    COUNT(*) AS track_count,
    ROUND(AVG(streams), 0) AS avg_streams -- How do they perform?
FROM spotify_tracks
GROUP BY quality_flag
ORDER BY track_count DESC;

-- Temporal trends
SELECT
    released_month,
    COUNT(*) as total_tracks,
    SUM(streams) AS total_streams
FROM spotify_tracks
GROUP BY released_month
ORDER BY total_streams DESC;

-- Musicality vs Success
SELECT 
    CASE 
        WHEN "danceability_%" > 75 THEN 'High Energy/Dance'
        WHEN "danceability_%" BETWEEN 50 AND 75 THEN 'Mid-Tempo'
        ELSE 'Slow/Chill'
    END AS song_vibe,
    COUNT(*) AS track_count,
    ROUND(AVG(streams), 0) AS avg_streams
FROM spotify_tracks
GROUP BY song_vibe
ORDER BY avg_streams DESC;
