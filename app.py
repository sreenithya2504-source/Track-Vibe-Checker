
import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
model = joblib.load("model/popularity_model.pkl")
age_tracks = pd.read_csv("data/top_tracks_by_age.csv")

# Load the Spotify dataset for song-name search
spotify_df = pd.read_csv(
    "data/spotify-tracks-dataset-detailed.csv"
)

spotify_df = spotify_df.dropna(
    subset=["artists", "track_name"]
)

# -----------------------------
# Page Title
# -----------------------------

st.title("🎵 Track Vibe Checker")

st.header("🎶 Predict Popularity by Song Name")

song_name = st.text_input("Enter song name")
artist_name = st.text_input("Enter artist name")

if st.button("Find Song and Predict"):

    if not song_name.strip() or not artist_name.strip():
        st.warning("Please enter both the song name and artist.")

    else:
        results = spotify_df[
            spotify_df["track_name"].str.contains(
                song_name.strip(),
                case=False,
                na=False,
                regex=False
            )
            &
            spotify_df["artists"].str.contains(
                artist_name.strip(),
                case=False,
                na=False,
                regex=False
            )
        ]

        if results.empty:
            st.error(
                "Song not found in the Spotify dataset. "
                "Try another spelling or use the audio-feature sliders below."
            )

        else:
            song = results.iloc[0]

            features = [
                "danceability",
                "energy",
                "loudness",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo"
            ]

            input_data = song[features].to_frame().T
            prediction = model.predict(input_data)[0]
            prediction = max(0, min(100, prediction))

            st.success(
                f"Found: {song['track_name']} — {song['artists']}"
            )

            st.metric(
                "Predicted Popularity",
                f"{prediction:.1f} / 100"
            )

            st.caption(
                "This is the model's prediction from the track's "
                "audio features, not a live popularity measurement."
            )

st.write(
    "Adjust the audio features of a song to predict its popularity "
    "and visualize its vibe."
)

# -----------------------------
# Audio Feature Inputs
# -----------------------------

danceability = st.slider("Danceability", 0.0, 1.0, 0.5)
energy = st.slider("Energy", 0.0, 1.0, 0.5)
loudness = st.slider("Loudness", -60.0, 5.0, -10.0)
speechiness = st.slider("Speechiness", 0.0, 1.0, 0.1)
acousticness = st.slider("Acousticness", 0.0, 1.0, 0.5)
instrumentalness = st.slider("Instrumentalness", 0.0, 1.0, 0.0)
liveness = st.slider("Liveness", 0.0, 1.0, 0.2)
valence = st.slider("Valence", 0.0, 1.0, 0.5)
tempo = st.slider("Tempo", 0.0, 250.0, 120.0)

# -----------------------------
# Popularity Prediction
# -----------------------------

if st.button("Predict Popularity"):

    input_data = pd.DataFrame([{
        "danceability": danceability,
        "energy": energy,
        "loudness": loudness,
        "speechiness": speechiness,
        "acousticness": acousticness,
        "instrumentalness": instrumentalness,
        "liveness": liveness,
        "valence": valence,
        "tempo": tempo
    }])

    prediction = model.predict(input_data)[0]
    prediction = max(0, min(100, prediction))

    st.subheader("📊 Predicted Popularity")

    st.metric(
        label="Popularity Score",
        value=f"{prediction:.1f} / 100"
    )

    # -----------------------------
    # Vibe Match Radar Chart
    # -----------------------------

    categories = [
        "Danceability",
        "Energy",
        "Acousticness",
        "Instrumentalness",
        "Liveness",
        "Valence"
    ]

    values = [
        danceability,
        energy,
        acousticness,
        instrumentalness,
        liveness,
        valence
    ]

    # Close the radar chart
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            name="Vibe"
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title="🎧 Vibe Match",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Age-Wise Listening Analysis
# -----------------------------

st.divider()

st.header("🎵 Age-Wise Listening Analysis")

st.write(
    "Explore tracks with the most recorded listening events "
    "among users in each age group in the Last.fm dataset."
)

age_group = st.selectbox(
    "Select an age group",
    [
        "Kids (5-12)",
        "Young (13-17)",
        "Adult (18-59)",
        "Elder (60-80)"
    ]
)

selected_tracks = age_tracks[
    age_tracks["age_group"] == age_group
].copy()

st.subheader(f"Top Tracks: {age_group}")

st.dataframe(
    selected_tracks[["artist", "track", "listens"]]
        .reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "These are observed Last.fm listening counts, not predictions "
    "of overall song popularity. Results are limited by the available "
    "user profiles and the small number of users in some age groups."
)

# -----------------------------
# Search for a Song
# -----------------------------

st.divider()

st.header("🔎 Search for a Song")

search_artist = st.text_input("Artist name")
search_track = st.text_input("Track name")

if st.button("Search Song"):

    # Check that at least one search field is filled
    if not search_artist.strip() and not search_track.strip():

        st.warning("Enter an artist name or track name to search.")

    else:

        # Start with all saved tracks
        matches = age_tracks.copy()

        # Filter by artist if provided
        if search_artist.strip():
            matches = matches[
                matches["artist"].str.contains(
                    search_artist.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        # Filter by track if provided
        if search_track.strip():
            matches = matches[
                matches["track"].str.contains(
                    search_track.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        if matches.empty:

            st.info(
                "No match found in the saved top-10 tracks. "
                "Try another spelling or search the age-wise tables."
            )

        else:

            st.subheader("Matching Age-Group Results")

            st.dataframe(
                matches[
                    ["age_group", "artist", "track", "listens"]
                ],
                use_container_width=True,
                hide_index=True
            )

            # -----------------------------
            # Listening Count Bar Chart
            # -----------------------------

            chart_data = matches.groupby(
                "age_group", as_index=False
            )["listens"].sum()

            st.subheader("📊 Listening Count by Age Group")

            st.bar_chart(
                chart_data,
                x="age_group",
                y="listens",
                x_label="Age Group",
                y_label="Recorded Listening Count"
            )

            if len(chart_data) == 1:
                st.info(
                    "This track appears in the saved top-10 list for "
                    "only one age group. This does not mean other age "
                    "groups never listened to it."
                )

            st.caption(
                "The chart uses saved top-10 track results only. "
                "It does not represent all listening events or "
                "a complete comparison of age-group preferences."
            )