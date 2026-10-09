import pandas as pd
from collections import Counter

profile_path = "data/userid-profile.tsv"

listening_path = r"C:\Users\malam\Downloads\lastfm-dataset-1K\lastfm-dataset-1K\userid-timestamp-artid-artname-traid-traname.tsv"

profiles = pd.read_csv(
    profile_path,
    sep="\t",
    header=None,
    skiprows=1,
    names=["user_id", "gender", "age", "country", "signup"]
)

profiles["age"] = pd.to_numeric(profiles["age"], errors="coerce")
profiles = profiles[profiles["age"].between(5, 80)].copy()

def assign_age_group(age):
    if 5 <= age <= 12:
        return "Kids (5-12)"
    elif 13 <= age <= 17:
        return "Young (13-17)"
    elif 18 <= age <= 59:
        return "Adult (18-59)"
    elif 60 <= age <= 80:
        return "Elder (60-80)"

profiles["age_group"] = profiles["age"].apply(assign_age_group)

columns = [
    "user_id", "timestamp", "artist_mbid",
    "artist_name", "track_mbid", "track_name"
]

age_lookup = profiles.set_index("user_id")["age_group"]
counters = {group: Counter() for group in profiles["age_group"].unique()}

for chunk in pd.read_csv(
    listening_path,
    sep="\t",
    header=None,
    names=columns,
    chunksize=100000,
    on_bad_lines="skip"
):
    chunk["age_group"] = chunk["user_id"].map(age_lookup)

    chunk = chunk.dropna(subset=["age_group", "artist_name", "track_name"])

    for group, part in chunk.groupby("age_group"):
        tracks = zip(part["artist_name"], part["track_name"])
        counters[group].update(tracks)

for group, counter in counters.items():
    print(f"\nTop 10 tracks for {group}:")
    for (artist, track), count in counter.most_common(10):
        print(f"{artist} — {track}: {count} listens")

# Save the results for later dashboard integration
rows = []
for group, counter in counters.items():
    for (artist, track), count in counter.most_common(10):
        rows.append({
            "age_group": group,
            "artist": artist,
            "track": track,
            "listens": count
        })

pd.DataFrame(rows).to_csv("data/top_tracks_by_age.csv", index=False)
print("\nSaved results to data/top_tracks_by_age.csv")