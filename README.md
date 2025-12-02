# HORECA Frozen Poultry Distributor Finder

**End-to-end automated pipeline to find frozen duck/chicken distributors supplying Asian restaurants across Germany, Spain, and France.**

## What This Does

This Python script:

1. **Scrapes** ~2,200–3,200 HORECA distributors using Google Maps Text Search API across 28 cities
2. **Deduplicates** records using fuzzy matching (removes branch duplicates, normalizes data)
3. **Classifies** leads via LLM (optional, identifies Vietnamese/Chinese focus + HORECA fit)
4. **Exports** a clean CSV with company name, address, phone, email, priority score

**Input:** 28 city locations + 4 search queries per country  
**Output:** 500–1,000+ qualified HORECA prospects with contact details  
**Cost:** ~$2–7 for scraping + ~$20–30 for classification (optional)  
**Time:** ~2–3 minutes API runtime + ~1 hour for review  

---

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Google Cloud account with billing enabled
- (Optional) OpenAI API key for AI classification

### 2. Clone/Download Files

Create a directory and place these files in it:

```
horeca_finder/
├── horeca_distributor_finder.py    (main script)
├── requirements.txt                 (Python dependencies)
├── .env.template                    (environment template)
└── README.md                        (this file)
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you want a specific Python version:

```bash
python3.10 -m pip install -r requirements.txt
```

### 4. Get Google Maps API Key

**a) Open Google Cloud Console:**
- Go to https://console.cloud.google.com/
- Create a new project (or use existing)

**b) Enable APIs:**
- Search for "Places API" → Enable it
- Search for "Maps JavaScript API" → Enable it

**c) Create API key:**
- Go to "Credentials" → "Create Credentials" → "API Key"
- Copy your API key

**d) Set up billing:**
- Go to "Billing" and link a payment method
- Google gives ~$200 free credits/month; this script costs ~$2–7

### 5. Configure Environment Variables

**Option A: Using .env file (Recommended)**

```bash
# Copy template
cp .env.template .env

# Edit .env with your actual keys
nano .env  # or use your editor
```

Fill in:
```
GOOGLE_MAPS_API_KEY=AIza...your...key...here
```

(Leave OPENAI_API_KEY blank for now; we'll skip AI classification initially)

**Option B: Set as environment variables directly**

```bash
export GOOGLE_MAPS_API_KEY="AIza...your...key...here"
python horeca_distributor_finder.py
```

### 6. Run the Script

```bash
python horeca_distributor_finder.py
```

Expected output:

```
🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 
HORECA FROZEN POULTRY DISTRIBUTOR FINDER
End-to-End Pipeline
🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 

======================================================================
PHASE 1: GOOGLE MAPS SCRAPING
======================================================================

🌍 Germany
  📍 Berlin (30km radius)
    🔍 Vietnamesische Lebensmittel Großhandel... (18 found)
    🔍 Chinesischer Lebensmittel Großhandel... (12 found)
    🔍 Asiatischer Tiefkühlkost Großhandel HORECA... (8 found)
    🔍 Frozen duck importer HORECA... (5 found)
  📍 Hamburg (30km radius)
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

```
id, company_name, street_address, city, postal_code, full_address,
latitude, longitude, phone, website, rating, review_count, types,
source, search_query, scrape_timestamp
```

**Example:**
```
id,company_name,street_address,city,postal_code,full_address,latitude,longitude,phone,website,rating,review_count,types,source,search_query,scrape_timestamp
ChIJxxx,Euro Asia Union,Steintorplatz 5,Hamburg,20095,"Steintorplatz 5, 20095 Hamburg, Germany",53.55,10.00,+49 40 1234567,https://euroasia.de,4.5,120,"restaurant,food,wholesale",google_maps_textsearch,"Vietnamese food wholesale",2025-12-02T10:30:00
```

**Use this CSV to:**
- Contact companies directly (phone + website)
- Filter by region/city
- Verify ratings/reviews
- Look up website for more info

---

## How to Use the Results

### 1. Open in Excel/Sheets

```bash
# On Mac
open FINAL_HORECA_PROSPECTS.csv

# On Windows
start FINAL_HORECA_PROSPECTS.csv

# Or upload to Google Sheets
```

### 2. Filter & Sort

- **Sort by rating** (high rating = more credible)
- **Filter by city** (focus on major hubs first)
- **Filter by website** (companies with websites = more established)

### 3. Outreach

For each company:

1. **Phone call** (direct, personal)
   - "Hi, we're importing crispy duck/chicken frozen products. Are you interested in samples?"
   - Ask for procurement manager

2. **Email** (formal, with details)
   - Use company website contact form if available
   - Reference you found them on Google Maps
   - Attach product brochure (images, certifications, pricing)

3. **LinkedIn** (B2B networking)
   - Search company name
   - Connect with procurement manager
   - Send product info

---

## Customization

### Add More Cities

Edit `SEARCH_LOCATIONS` in the script:

```python
"Germany": {
    "tier_1": [
        {"name": "Your City", "lat": 52.00, "lng": 13.00, "radius": 30},
    ]
}
```

Get coordinates from Google Maps (right-click → copy coordinates).

### Change Search Queries

Edit `SEARCH_QUERIES`:

```python
"Germany": [
    "Your custom query",
    "Another query",
]
```

### Enable AI Classification

To classify leads by priority (1–10 score):

1. Get OpenAI API key: https://platform.openai.com/api-keys
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
3. In script, set:
   ```python
   ENABLE_AI_CLASSIFICATION = True
   ```
4. Run again

**Cost:** ~$20–30 for 1,000 classifications

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
- API not enabled (go to Cloud Console → enable "Places API")
- Search query too specific (try broader queries)

### Error: "fuzzywuzzy import failed"

**Solution:** Install missing package

```bash
pip install fuzzywuzzy python-Levenshtein
```

### Script running too slow?

- Reduce `MAX_PAGES_PER_QUERY` from 3 to 2 (limits results to 40 per search)
- Remove some cities from `SEARCH_LOCATIONS`
- Run during off-peak hours (less API latency)

---

## Cost Breakdown

| Component | Cost |
|-----------|------|
| Google Maps Text Search API | $0.0145 per query |
| Example: 112 queries × 2 pages | ~$3–5 |
| OpenAI classification (optional) | $0.001–0.003 per classification |
| Example: 1,000 classifications | ~$20–30 |
| **Total (with classification)** | ~$25–35 |
| **Total (without classification)** | ~$3–5 |

Google provides $200 free monthly credits for new accounts.

---

## Data Privacy & GDPR

✅ **This script respects GDPR:**
- Only scrapes **public** Google Maps data
- No personal data (PII) collected
- No cookies or tracking
- Data stored locally, not shared

**Note:** When you contact companies, **you must comply with GDPR:**
- Don't spam (B2B outreach is OK if business-related)
- Include unsubscribe option in emails
- Don't sell contact list to third parties

---

## Next Steps

1. **Run the script** → generates CSV
2. **Review top 20–30** entries manually
3. **Reach out to top prospects** with product samples
4. **Refine search queries** based on results
5. **Iterate** (run again with adjusted queries after 2–4 weeks)

---

## Support & Debugging

If script fails:

1. **Check API key:**
   ```bash
   grep GOOGLE_MAPS_API_KEY .env
   ```

2. **Check Google Cloud:**
   - Go to console.cloud.google.com
   - Check billing is enabled
   - Check API quotas (Quotas → Places API)

3. **Check network:**
   ```bash
   ping maps.googleapis.com
   ```

4. **Run in verbose mode** (add print statements to debug)

---

## Files Overview

```
horeca_distributor_finder.py
├── Config class           - Settings & API keys
├── SEARCH_LOCATIONS       - 28 cities with coordinates
├── SEARCH_QUERIES         - Localized search terms
├── GoogleMapsScraper      - Phase 1: Scraping
├── Deduplicator           - Phase 2: Deduplication
├── AIClassifier           - Phase 3: AI classification
├── FileManager            - CSV I/O
└── main()                 - Orchestration

Output files:
├── 1_raw_leads.csv                    (raw API results)
├── 2_deduped_leads.csv                (deduplicated)
├── FINAL_HORECA_PROSPECTS.csv         (ready for outreach) ← USE THIS
└── (3_classified_leads.csv)           (if AI enabled)
```

---

## License

This script is for internal business use. Do not resell the data or use for spam.

---

## Contact & Questions

For issues or questions about the script, check:
- Google Maps API docs: https://developers.google.com/maps/documentation/places
- OpenAI docs: https://platform.openai.com/docs
- FuzzyWuzzy docs: https://github.com/seatgeek/fuzzywuzzy

---

**Last updated:** December 2, 2025
**Status:** Production-ready ✅
