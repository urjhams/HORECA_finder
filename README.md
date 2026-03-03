# Germany Restaurant Finder - B2B Supplies

**End-to-end automated pipeline to find Chinese, Vietnamese, and Turkish restaurants across Germany for selling hand towels and paper boxes.**

## What This Does

This Python script:

1. **Scrapes** restaurants across 32 German cities using Google Maps Text Search API
2. **Deduplicates** records using fuzzy matching (handles restaurant chains correctly)
3. **Classifies** restaurants via AI (Gemini) into Chinese, Vietnamese, Turkish categories
4. **Exports** separate CSV files by restaurant type with contact details and fit scores

**Target:** Small-medium restaurants, bistros, quick-service establishments  
**Products:** Hand towels (paper towels) and paper boxes (takeaway packaging)  
**Input:** 32 German cities (4 coverage tiers) + 4 restaurant search queries  
**Output:** Categorized restaurant lists ready for B2B outreach  
**Cost:** ~$5–10 for scraping + ~$2–5 for AI classification (with Gemini)  
**Time:** ~5–10 minutes API runtime + classification time  

---

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Google Cloud account with billing enabled
- (Optional) Google Gemini API key for AI classification

### 2. Clone Repository

```bash
git clone <repository-url>
cd HORECA_finder
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or with virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
```

### 4. Get Google Maps API Key

**a) Open Google Cloud Console:**
- Go to https://console.cloud.google.com/
- Create a new project (or use existing)

**b) Enable APIs:**
- Search for "Places API (New)" → Enable it

**c) Create API key:**
- Go to "Credentials" → "Create Credentials" → "API Key"
- Copy your API key

**d) Set up billing:**
- Go to "Billing" and link a payment method
- Google gives ~$200 free credits/month; this script costs ~$5–10

### 5. (Optional) Get Google Gemini API Key

**For AI classification only:**
- Go to https://aistudio.google.com/app/apikey
- Click "Create API Key"
- Copy your API key

### 6. Configure Environment Variables

```bash
# Copy template
cp env.template .env

# Edit .env with your actual keys
nano .env  # or use your editor
```

Fill in:
```
GOOGLE_MAPS_API_KEY=AIza...your...key...here
GEMINI_API_KEY=your_gemini_api_key_here  # Optional - for AI classification
```

### 7. Run the Script

**Basic Usage (Scraping Only):**
```bash
python src/horeca_distributor_finder.py
```

**With AI Classification:**
```bash
python src/horeca_distributor_finder.py --ai-classify
```

**Advanced Options:**

1. **Specify Output Directory:**
   ```bash
   python src/horeca_distributor_finder.py my_project
   ```

2. **Resume from Previous Run:**
   ```bash
   python src/horeca_distributor_finder.py --resume --ai-classify
   ```

Expected output:

```
🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 
GERMANY RESTAURANT FINDER - B2B SUPPLIES
Find Chinese, Vietnamese & Turkish Restaurants
🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 

======================================================================
PHASE 1: GOOGLE MAPS SCRAPING
======================================================================

🌍 Germany
  📍 Berlin-Center (10km radius)
    🔍 Restaurant... (156 found)
    🔍 Asiatisches Restaurant... (89 found)
    🔍 Vietnamesisches Restaurant... (45 found)
    🔍 Chinesisches Restaurant... (67 found)
  📍 Hamburg-Center (10km radius)
    ...
```

When complete, it will save 4 CSV files:
- `1_raw_leads.csv` - Raw results from Google Maps
- `2_deduped_leads.csv` - After deduplication
- `FINAL_HORECA_PROSPECTS.csv` - **MAIN FILE** (clean, ready for outreach)

---

## Output Files

### FINAL_HORECA_PROSPECTS.csv

Main file with columns:

When complete, it will save CSV files:
- `1_raw_restaurants.csv` - Raw results from Google Maps
- `2_deduped_restaurants.csv` - After deduplication
- `FINAL_RESTAURANT_PROSPECTS.csv` - **MAIN FILE** (all target restaurants)

With AI classification enabled:
- `3_classified_restaurants.csv` - With AI analysis
- `FINAL_CHINESE_RESTAURANTS.csv` - Chinese restaurants only
- `FINAL_VIETNAMESE_RESTAURANTS.csv` - Vietnamese restaurants only
- `FINAL_TURKISH_RESTAURANTS.csv` - Turkish restaurants only

---

## Output Files

### Main Output Files (with AI Classification)

**FINAL_CHINESE_RESTAURANTS.csv** - Chinese restaurants
**FINAL_VIETNAMESE_RESTAURANTS.csv** - Vietnamese restaurants  
**FINAL_TURKISH_RESTAURANTS.csv** - Turkish restaurants  
**FINAL_RESTAURANT_PROSPECTS.csv** - All target restaurants combined

Columns:
```
id, company_name, street_address, city, postal_code, full_address,
latitude, longitude, phone, website, rating, review_count, types,
restaurant_type, business_model, is_target_customer, product_fit_score,
reasoning, contact_recommendation, source, search_query, scrape_timestamp
```

**Example:**
```csv
id,company_name,city,phone,website,rating,restaurant_type,business_model,product_fit_score,reasoning,contact_recommendation
ChIJxxx,Pho Vietnam Bistro,Berlin,+49 30 1234567,https://pho-vietnam.de,4.5,Vietnamese,bistro,9,"Vietnamese bistro likely has high takeaway volume",High priority
ChIJyyy,Döner Kebab Express,Hamburg,+49 40 9876543,https://doener-express.de,4.2,Turkish,quick-service,8,"Turkish quick-service high packaging needs",High priority
```

**Use these CSVs to:**
- Contact restaurants directly (phone)
- Visit restaurant websites for more info
- Target by cuisine type for customized pitches
- Sort by product_fit_score for priority outreach
- Import to CRM for sales campaigns

---

## How to Use the Results

### 1. Open in Excel/Sheets

```bash
# On Mac
open FINAL_CHINESE_RESTAURANTS.csv

# On Windows  
start FINAL_VIETNAMESE_RESTAURANTS.csv

# Or upload to Google Sheets
```

### 2. Filter & Sort

- **Sort by product_fit_score** (highest = best prospects)
- **Filter by city** (focus on your target region)
- **Filter by business_model** (bistro/quick-service = high takeaway volume)
- **Check contact_recommendation** (High/Medium/Low priority)

### 3. Outreach Strategy

**For Chinese Restaurants:**
- Products: Packaging for dim sum, spring rolls, fried rice takeaway
- Pitch: "We supply high-quality paper boxes perfect for Chinese takeaway"

**For Vietnamese Restaurants:**
- Products: Pho containers, spring roll boxes, bánh mì packaging
- Pitch: "Specialty packaging for Vietnamese cuisine takeaway orders"

**For Turkish Restaurants:**
- Products: Döner boxes, wrap containers, kebab packaging
- Pitch: "Premium packaging solutions for döner and kebab businesses"

**Contact Methods:**

1. **Phone call** (most effective)
   - "Hi, we supply hand towels and takeaway packaging for restaurants"
   - Ask for owner or manager
   - Offer free samples

2. **Website contact form** (if available)
   - Professional message with product catalog
   - Mention you found them on Google Maps
   - Include pricing and volume discounts

3. **Visit in person** (local restaurants)
   - Bring product samples
   - Show catalog and pricing
   - Build relationship

---

## Customization

### Add More Cities

Edit `src/search_config_horeca.py`:

```python
"tier_1_mega": [
    {"name": "Your City", "lat": 52.00, "lng": 13.00, "radius": 10},
]
```

Get coordinates from Google Maps (right-click → copy coordinates).

### Change Search Queries

Edit `SEARCH_QUERIES` in `src/search_config_horeca.py`:

```python
"Germany": [
    "Restaurant",
    "Your custom query",
]
```

### Adjust Classification Criteria

In `src/horeca_distributor_finder.py`, modify filtering:

```python
# Change minimum product fit score
product_fit_score >= 7  # Instead of 5 (more selective)

# Remove phone requirement
# and r.get("phone")  # Comment out this line
```

---

## AI Classification Details

The script uses **Google Gemini** for classification with optimized batch processing.

### Batch Size Optimization

- **Batch Size: 40** (processes 40 restaurants per API call)
- **Why 40?** Maximum efficiency with Gemini
  - Reduces API calls by 97.5% (vs single-record processing)
  - Lower cost per classification (~$0.001 per restaurant)
  - Fast response time
  - Reliable JSON parsing

### Classification Fields

For each restaurant, AI determines:
- `restaurant_type`: Chinese, Vietnamese, Turkish, Other, Not a Restaurant
- `business_model`: bistro, quick-service, gastronomy, fine-dining, cafe, other
- `is_target_customer`: true/false (good fit for supplies?)
- `product_fit_score`: 1-10 (likelihood to buy packaging)
- `reasoning`: Brief explanation
- `contact_recommendation`: High/Medium/Low priority

---

## Troubleshooting

### Error: "GOOGLE_MAPS_API_KEY not configured"

**Solution:** Check `.env` file exists and has correct key format

```bash
cat .env  # Check contents
```

### Error: "quota exceeded" or "zero results"

**Causes:**
- API quotas reached (Google gives $200/month free; check billing)
- API not enabled (go to Cloud Console → enable "Places API (New)")
- Search query too specific (try broader queries)

### Error: "google-genai import failed"

**Solution:** Install missing package

```bash
pip install google-genai
```

### Script running too slow?

- Reduce search locations in `src/search_config_horeca.py`
- Skip AI classification (run without `--ai-classify`)
- Run during off-peak hours (less API latency)

---

## Cost Breakdown

| Component | Cost per Unit | Example Usage | Total |
|-----------|---------------|---------------|-------|
| Google Maps Text Search API | $0.032 per search | 128 searches (32 cities × 4 queries) | ~$4 |
| Google Maps Text Search API | $0.017 per result | ~1,000 results | ~$17 |
| Google Gemini Classification | ~$0.001 per restaurant | 1,000 restaurants (40 per batch) | ~$1-2 |
| **Total (with classification)** | | | **~$22-23** |
| **Total (without classification)** | | | **~$21** |

**Note:** Google provides $200 free monthly credits for new accounts.

---

## Data Privacy & GDPR

✅ **This script respects GDPR:**
- Only scrapes **public** Google Maps data
- No personal data (PII) collected
- No cookies or tracking
- Data stored locally, not shared

**Note:** When you contact restaurants, **you must comply with GDPR:**
- B2B outreach is OK if business-related
- Keep communications professional
- Respect opt-out requests
- Don't sell contact list to third parties

---

## Next Steps

1. **Run the script** → generates categorized CSV files
2. **Review top prospects** by product_fit_score
3. **Reach out by restaurant type** with targeted pitches
4. **Track responses** and conversion rates
5. **Iterate** based on results (adjust cities/queries)

---

## Project Structure

```
HORECA_finder/
├── src/
│   ├── horeca_distributor_finder.py  - Main script
│   ├── google_maps_scraper.py        - Google Maps API integration
│   ├── ai_classifier.py              - Gemini AI classification
│   ├── utils.py                      - Deduplication & reporting
│   ├── search_config_horeca.py       - Location & query config
│   └── search_config_nrw_warehouse.py - (legacy)
├── requirements.txt                   - Python dependencies
├── env.template                       - Environment template
├── README.md                          - This file
└── .env                              - Your API keys (create from template)

Output files (after running):
├── 1_raw_restaurants.csv             - Raw Google Maps data
├── 2_deduped_restaurants.csv         - After deduplication
├── 3_classified_restaurants.csv      - After AI classification
├── FINAL_CHINESE_RESTAURANTS.csv     - Chinese restaurants only
├── FINAL_VIETNAMESE_RESTAURANTS.csv  - Vietnamese restaurants only
├── FINAL_TURKISH_RESTAURANTS.csv     - Turkish restaurants only
└── FINAL_RESTAURANT_PROSPECTS.csv    - All target restaurants
```

---

## Pipeline Overview

**Phase 1: Scraping**
- Google Maps Text Search API
- 32 German cities (4 tiers: mega/large/regional/gaps)
- 4 search queries: Restaurant, Asian, Vietnamese, Chinese
- ~1,000-3,000 raw results

**Phase 2: Deduplication**
- Fuzzy name matching (85% threshold)
- Phone/website matching
- Handles restaurant chains (same name, different cities)
- ~800-2,000 unique restaurants

**Phase 3: AI Classification (Optional)**
- Google Gemini 2.5 Flash Lite
- Batch size: 40 restaurants per call
- Classifies: Chinese/Vietnamese/Turkish/Other
- Scores: product_fit_score (1-10)
- ~500-1,000 target restaurants

**Phase 4: Export by Type**
- Filters: score ≥5, has phone, is_target_customer
- Separate CSV files per restaurant type
- Sorted by product_fit_score
- Ready for B2B outreach

---

## License

This script is for internal business use. Do not resell the data or use for spam.

---

## Contact & Questions

For issues or questions:
- Google Maps API docs: https://developers.google.com/maps/documentation/places
- Google Gemini docs: https://ai.google.dev/docs
- FuzzyWuzzy docs: https://github.com/seatgeek/fuzzywuzzy

---

**Last updated:** March 3, 2026  
**Status:** Production-ready ✅

