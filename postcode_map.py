import pandas as pd
import folium
import requests

# Load your postcode data
df = pd.read_csv("postcodes.csv")

# Clean the postcode column
df["postcode"] = df["postcode"].str.upper().str.strip()

# Count how many times each postcode appears
popularity = (
    df.groupby("postcode")
      .size()
      .reset_index(name="popularity")
)

# Get latitude and longitude for each postcode
def get_coordinates(postcode):

    url = f"https://api.postcodes.io/postcodes/{postcode.replace(' ', '')}"

    response = requests.get(url)

    if response.status_code == 200:
        result = response.json()["result"]

        return pd.Series([
            result["latitude"],
            result["longitude"]
        ])

    return pd.Series([None, None])


# Get coordinates
popularity[["latitude", "longitude"]] = (
    popularity["postcode"].apply(get_coordinates)
)

# Create UK map
m = folium.Map(
    location=[52.5, -1.5],
    zoom_start=6
)

# Find the highest popularity
max_popularity = popularity["popularity"].max()

# Add postcode markers
for _, row in popularity.dropna(
    subset=["latitude", "longitude"]
).iterrows():

    radius = 5 + (
        row["popularity"] / max_popularity
    ) * 25

    folium.CircleMarker(
        location=[
            row["latitude"],
            row["longitude"]
        ],
        radius=radius,
        popup=(
            f"Postcode: {row['postcode']}<br>"
            f"Popularity: {row['popularity']}"
        ),
        fill=True,
        fill_opacity=0.7
    ).add_to(m)

# Save the map
m.save("postcode_map.html")

print("Map created successfully!")
