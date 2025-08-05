Apartment Analysis Project

Project Scope
Goal: Identify and rank apartments based on location, space, amenities, and lifestyle quality.

Inputs:
- Excel file with Apartment Name, Neighborhood, Price, Listing Link

Outputs:
1. Apartment_Search_Enriched.xlsx with SqFt, Pool/Gym flags, Price per SqFt, Lifestyle Score, and
Rank

2. Interactive Maps (Apartments_Map.html, Apartments_Map_Color.html)
Transformations & Thought Process
 
Scraping & Feature Extraction:
- SqFt parsed from page text
- Has Pool (Y/N)
- Has Gym (Y/N)

Derived Metrics:
- Price/SqFt = Total Rent ÷ SqFt
- BeachScore = Weighted inverse distance to the beach
- WalkScore = Estimated from neighborhood walkability
- PriceScore = Normalized inverse of Price per SqFt

Lifestyle Score Formula:
Lifestyle Score = (0.40 × BeachScore) + (0.35 × WalkScore/100) + (0.25 × PriceScore)

Reasoning:
- Beach Proximity (40%)
- Walkability & Amenities (35%)
- Price Efficiency (25%)


Terminal Instructions
1 Navigate to Project Folder:
cd "/Users/Milan/Desktop/python test"
2 Create Virtual Environment:
python3 -m venv env
source env/bin/activate
3 Install Libraries:
pip3 install selenium pandas openpyxl folium matplotlib
4 Run the Scraper:
python3 scrape_apartments_selenium.py
5 Run the Mapping Script:
python3 map_apartments.py
6 Analyze Results:
- Filter SqFt ≥ 1000 in Excel
- Sort by Lifestyle Score
- Open Apartments_Map_Color.html to visualize apartments

Deliverables
- Apartment_Search_Enriched.xlsx → Full dataset with Lifestyle Scores
- Apartments_Map_Color.html → Interactive, color-coded map
- Top 5 apartments → Easily identified via Rank and green markers

Decision Making
Use the Excel ranking and interactive map to quickly decide:
- Which apartments have the best lifestyle fit
- Which are closest to the beach with high walkability
- Which provide the best value for space
