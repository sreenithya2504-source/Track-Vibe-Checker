
import pandas as pd

file_path = r"C:\Users\malam\Downloads\lastfm-dataset-1K\lastfm-dataset-1K\userid-timestamp-artid-artname-traid-traname.tsv"

columns = [
    "user_id",
    "timestamp",
    "artist_mbid",
    "artist_name",
    "track_mbid",
    "track_name"
]

df = pd.read_csv(
    file_path,
    sep="\t",
    header=None,
    names=columns,
    nrows=5,
    on_bad_lines="skip"
)

print("First 5 listening records:")
print(df.to_string(index=False))

print("\nColumn names:")
print(df.columns.tolist())