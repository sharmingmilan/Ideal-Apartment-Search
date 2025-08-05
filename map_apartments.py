import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
import os
import webbrowser

# File paths
file_path = "/Users/Milan/Desktop/pythontest/Apartment Search September.xlsx"
cache_path = "/Users/Milan/Desktop/pythontest/apartment_geocode_cache.csv"
output_map = "/Users/Milan/Desktop/pythontest/apartments_map.html"

# Load apartment data
df = pd.read_excel(file_path, sheet_name="Sheet1")

# Check for cached coordinates
if os.path.exists(cache_path):
    cache_df = pd.read_csv(cache_path)
    df = df.merge(cache_df, on="Apartment Name", how="left")
else:
    # Initialize geocoder
    geolocator = Nominatim(user_agent="apartment_mapper")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # Geocode apartments
    df["location"] = df["Apartment Name"].apply(geocode)
    df["latitude"] = df["location"].apply(lambda loc: loc.latitude if loc else None)
    df["longitude"] = df["location"].apply(lambda loc: loc.longitude if loc else None)

    # Save cache
    df[["Apartment Name", "latitude", "longitude"]].to_csv(cache_path, index=False)

# Drop apartments without coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Center map on the first apartment
map_center = [df["latitude"].iloc[0], df["longitude"].iloc[0]]
apartment_map = folium.Map(location=map_center, zoom_start=12)

# Add yellow star markers
for _, row in df.iterrows():
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=f"{row['Apartment Name']}<br>Price: ${row['Price (Total)']}",
        icon=folium.Icon(color="yellow", icon="star")
    ).add_to(apartment_map)

# Save map to HTML
apartment_map.save(output_map)

# Open in browser
webbrowser.open(f"file://{output_map}")

print(f"✅ Map generated: {output_map}")
print("💡 Opening in browser...")
