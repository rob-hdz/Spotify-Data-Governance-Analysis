# Data Quality Rules

| Rule ID | Feature | Logic/Check | Action if fails |
| ------- | ------- | ----------- | --------------- |
| DQ-01 | `track_name`<br> `artist(s)_name` | Must not be empty or `Null` | **REJECT** (Drop row) |
| DQ-02 | `streams` | Must be Numeric and `≥0` | **REJECT** (Drop row) |
| DQ-08 | `danceability_%` <br> `valence_%` <br> `energy_%` <br> `acousticness_%` <br> `instrumentalness_%` <br> `liveness_%` <br> `speechiness_%` | Range [`0`,`100`] | **REJECT** (Out of bounds) |
| DQ-07 | `bpm` | Range [`40`,`250`] | **FLAG** (Keep, but add 'Review' tag) |
| DQ-03 | `artist_count` | Must be Numeric and `≥1` | **TRANSFORM** (Set to `Null`) |
| DQ-04 | `released_year` <br> `released_month` <br> `released_day` | Range [`1900`,`2026`] <br> Range [`1`,`12`] <br> Range [`1`,`31`] | **TRANSFORM** (Set to `Null`) |
| DQ-05 | `key` | Must be in defined Set {`C`,`C#`,`D`,`D#`,`E`,`F`,`F#`,`G`,`G#`,`A`,`A#`,`B`} | **TRANSFORM** (Set to `Null`) |
| DQ-06 | `mode` | Must be in defined Set {`Major`,`Minor`} | **TRANSFORM** (Set to `Null`) |
| DQ-09 | `in_spotify_playlists` <br> `in_spotify_charts` <br> `in_apple_playlists` <br> `in_apple_charts` <br> `in_deezer_playlists` <br> `in_deezer_charts` <br> `in_shazam_charts` | Must be Numeric and `≥0` | **TRANSFORM** (Set to `0`) |

&ensp;

Note: Only **REJECT** (drop) if the missing data makes the row useless for my primary goal (like a song with no name) or if data is corrupted (like a percentage greater than 100).
