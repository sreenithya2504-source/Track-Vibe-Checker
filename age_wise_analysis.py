
import pandas as pd

profile_path = "data/userid-profile.tsv"

listening_path = r"C:\Users\malam\Downloads\lastfm-dataset-1K\lastfm-dataset-1K\userid-timestamp-artid-artname-traid-traname.tsv"

# Load user profiles
profiles = pd.read_csv(
    profile_path,
    sep="\t",
    header=None,
    skiprows=1,
    names=["user_id", "gender", "age", "country", "signup"]
)

profiles["age"] = pd.to_numeric(profiles["age"], errors="coerce")

# Keep only users aged 5 to 80
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

# Read listening records in manageable chunks
columns = [
    "user_id", "timestamp", "artist_mbid",
    "artist_name", "track_mbid", "track_name"
]

group_counts = {}
total_records = 0

for chunk in pd.read_csv(
    listening_path,
    sep="\t",
    header=None,
    names=columns,
    chunksize=100000,
    on_bad_lines="skip"
):
    matched = chunk[["user_id"]].merge(
        profiles[["user_id", "age_group"]],
        on="user_id",
        how="inner"
    )

    counts = matched["age_group"].value_counts()

    for group, count in counts.items():
        group_counts[group] = group_counts.get(group, 0) + int(count)

    total_records += len(chunk)

    print("Records processed:", total_records)

print("\nListening records by age group:")
for group in [
    "Kids (5-12)",
    "Young (13-17)",
    "Adult (18-59)",
    "Elder (60-80)"
]:
    print(group, ":", group_counts.get(group, 0))