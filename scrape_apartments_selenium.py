import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# === CONFIG ===
INPUT_FILE = "Apartment Search September.xlsx"
OUTPUT_FILE = "Apartment_Search_Enriched.xlsx"
SHEET_NAME = "Sheet1"

# === Load Excel ===
df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

# Add columns
#I wanted to add more metrics for better decision making

for col in ["SqFt", "Has Pool", "Has Gym", "Price/SqFt", "BeachScore", "WalkScore", "Lifestyle Score"]:
    if col not in df.columns:
        df[col] = None

# === Neighborhood scores ===
# scores based off of closeness to the beach and public transpo routes

distance_map = {
    "Venice": 1, "Santa Monica": 1, "Marina Del Rey": 1,
    "Del Rey": 2, "West LA": 2, "Sawtelle": 2,
    "Palms": 3, "Culver City": 3, "Cheviot Hills": 3, "Century City": 3,
    "Westwood": 4, "Brentwood": 4,
    "Beverlywood": 5, "Mid Wilshire": 5, "Pico-Robertson": 5
}
walkscore_map = {
    "Venice": 92, "Santa Monica": 91, "Marina Del Rey": 84,
    "Del Rey": 80, "West LA": 78, "Sawtelle": 80,
    "Palms": 75, "Culver City": 78, "Cheviot Hills": 70,
    "Century City": 74, "Westwood": 82, "Brentwood": 80,
    "Beverlywood": 70, "Mid Wilshire": 80, "Pico-Robertson": 77
}

# === Configure Selenium ===
options = Options()
options.headless = True  # run without opening a browser window
driver = webdriver.Chrome(options=options)

def scrape_listing(url):
    try:
        driver.get(url)
        time.sleep(3)  # Allow page to load fully (maybe needs to be troubleshot)

        page_text = driver.page_source.lower()
        
        # --- Extract square footage ---
        sqft = None
        for token in ["sq ft", "sqft", "square feet"]:
            if token in page_text:
                snippet = page_text.split(token)[0][-20:]  # last 20 chars before token
                digits = ''.join([c if c.isdigit() else ' ' for c in snippet])
                numbers = [int(n) for n in digits.split() if n.isdigit()]
                if numbers:
                    sqft = max(numbers)
                    break

        # --- Pool/Gym? ---
        has_pool = "pool" in page_text
        has_gym = any(word in page_text for word in ["gym", "fitness center", "fitness studio"])

        return sqft, "Y" if has_pool else "N", "Y" if has_gym else "N"

    except Exception:
        return None, None, None

# === Loop through apartments ===
for idx, row in df.iterrows():
    url = row.get("Link", None)
    apt_name = row.get("Apartment Name", "Unknown")

    if pd.isna(url):
        print(f"[{idx+1}/{len(df)}] Skipped: {apt_name} (No link)")
        continue

    sqft, pool, gym = scrape_listing(url)
    df.at[idx, "SqFt"] = sqft
    df.at[idx, "Has Pool"] = pool
    df.at[idx, "Has Gym"] = gym

    if sqft and sqft > 0:
        df.at[idx, "Price/SqFt"] = row["Price (Total)"] / sqft

    # Add static scores
    neighborhood = row["Neighborhood"]
    df.at[idx, "BeachScore"] = 6 - distance_map.get(neighborhood, 5)
    df.at[idx, "WalkScore"] = walkscore_map.get(neighborhood, 70)

    print(f"[{idx+1}/{len(df)}] {apt_name} | SqFt: {sqft} | Pool: {pool} | Gym: {gym}")

# Close the driver
driver.quit()

# === Compute Lifestyle Score (adjust for apartment preferences -- plus more metrics?) ===
price_norm = df["Price/SqFt"].max()
df["PriceScore"] = 1 - (df["Price/SqFt"] / price_norm)
df["Lifestyle Score"] = (
    df["BeachScore"] * 0.4 +
    (df["WalkScore"] / 100) * 0.35 +
    df["PriceScore"] * 0.25
)

# Filter 1000+ sq ft and rank
df_filtered = df[df["SqFt"].fillna(0) >= 1000]
df_filtered = df_filtered.sort_values(by="Lifestyle Score", ascending=False)
df_filtered.insert(0, "Rank", range(1, len(df_filtered)+1))

# Save results
df_filtered.to_excel(OUTPUT_FILE, index=False)
print(f"\n Done! Enriched file saved as {OUTPUT_FILE}")
