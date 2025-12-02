# QUICK START GUIDE (5 minutes)

## TL;DR - Just run this:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and edit .env
cp .env.template .env
# Edit .env, add your Google Maps API key

# 3. Run the script
python horeca_distributor_finder.py

# 4. Open the results
# Results will be in: FINAL_HORECA_PROSPECTS.csv
```

---

## Step-by-Step (with screenshots)

### Step 1: Get Google Maps API Key (5 min)

1. Go to **https://console.cloud.google.com/**
2. Click **"Create Project"**
3. Name it: "HORECA Finder"
4. Go to **APIs & Services** → **Library**
5. Search for **"Places API"** → Click → **Enable**
6. Search for **"Maps JavaScript API"** → Click → **Enable**
7. Go to **Credentials** → **Create Credentials** → **API Key**
8. Copy the key (looks like: `AIza...`)
9. Paste into `.env` file:
   ```
   GOOGLE_MAPS_API_KEY=AIza...your...key...
   ```

### Step 2: Install Python Packages

```bash
pip install -r requirements.txt
```

**What it installs:**
- `requests` - for API calls
- `fuzzywuzzy` - for deduplication
- `python-dotenv` - for .env file reading

### Step 3: Run the Script

```bash
python horeca_distributor_finder.py
```

**You'll see:**
```
🚀 🚀 🚀 🚀 🚀 HORECA FROZEN POULTRY DISTRIBUTOR FINDER 🚀 🚀 🚀 🚀

======================================================================
PHASE 1: GOOGLE MAPS SCRAPING
======================================================================

🌍 Germany
  📍 Berlin (30km radius)
    🔍 Vietnamesische Lebensmittel Großhandel... (18 found)
    ...

======================================================================
PHASE 2: DEDUPLICATION & NORMALIZATION
======================================================================

📊 Input: 2,847 records
📊 Output: 1,932 unique records
🗑️  Duplicates removed: 915

======================================================================
FINAL SUMMARY REPORT
======================================================================

Total prospects: 1,932

By country:
  Germany: 842
  Spain: 531
  France: 559
```

### Step 4: Open Results

The script creates 4 files:

```
1_raw_leads.csv                    ← Raw results from API
2_deduped_leads.csv                ← After removing duplicates  
3_classified_leads.csv             ← (only if AI enabled)
FINAL_HORECA_PROSPECTS.csv         ← ⭐ USE THIS FILE
```

**Open the final file:**

```bash
# Mac
open FINAL_HORECA_PROSPECTS.csv

# Windows
start FINAL_HORECA_PROSPECTS.csv

# Linux
xdg-open FINAL_HORECA_PROSPECTS.csv

# Or upload to Google Sheets:
# 1. Go to https://sheets.google.com
# 2. File → Import → Upload → Select FINAL_HORECA_PROSPECTS.csv
# 3. Click "Import"
```

---

## What You Get

Each row has:
- **company_name** - Name of distributor
- **street_address** - Street address
- **city** - City
- **postal_code** - Zip code
- **phone** - Phone number (for cold calls!)
- **website** - Website URL
- **rating** - Google Maps rating (4.5★ = good)
- **review_count** - Number of reviews

**Example row:**
```
Euro Asia Union, Steintorplatz 5, Hamburg, 20095, Germany,
+49 40 12345678, https://euroasia.de, 4.5, 128
```

---

## What to do with the list

### Option 1: Manual Outreach
- Call the phone number
- Ask for "Einkauf" (Procurement Manager)
- Pitch: "We have high-quality frozen crispy duck/chicken. Can I send samples?"

### Option 2: Email Campaign
- Use the website to find contact form
- Send professional email with:
  - Product catalog
  - Certifications (FDA, Halal, etc.)
  - Pricing
  - Minimum order quantity
  - Lead time

### Option 3: LinkedIn Outreach
- Search company name on LinkedIn
- Find procurement manager
- Send connection request + message

---

## Troubleshooting

**Q: Script says "GOOGLE_MAPS_API_KEY not configured"**

A: Make sure:
1. `.env` file exists in same directory as script
2. It contains your actual API key (not "your_key_here")
3. Check for typos

```bash
cat .env  # Show contents
```

**Q: "quota exceeded" error**

A: Google Maps API costs money. Check:
1. Billing is enabled: https://console.cloud.google.com/billing
2. You have a payment method
3. Check your quota: https://console.cloud.google.com/apis/dashboard

(Google gives $200/month free; this costs ~$2–5)

**Q: Takes too long**

A: The script sleeps 1 second between API calls (to avoid throttling).
- 112 queries × 1 sec ≈ 2 minutes
- This is normal and expected
- Don't interrupt it

**Q: Getting 0 results for some cities**

A: Google Maps sometimes has limited results for niche queries. Try:
1. Broader search term (remove "frozen" or "HORECA")
2. Add neighboring cities
3. Check if businesses exist in that region

---

## Cost Check

Before you run (optional):

```bash
# Estimated cost:
# 28 cities × 4 queries × 2 pages = 224 API calls
# 224 × $0.0145 = $3.25

# This comes from your Google Cloud billing
# You get $200/month free, so this is free for first month
```

---

## Next: Analyze Results

After script completes, you have 1,000+ prospects. Now:

1. **Filter by rating** (keep 4.0+)
2. **Filter by country** (focus on Germany first)
3. **Sort by review count** (more reviews = more credible)
4. **Export top 20–30** for initial outreach

---

## Need Help?

1. Check README.md for detailed info
2. Check Google Maps API docs: https://developers.google.com/maps
3. Check script errors in console (copy & paste into Google)

---

**Ready? Run this:**

```bash
pip install -r requirements.txt
python horeca_distributor_finder.py
```

Then open `FINAL_HORECA_PROSPECTS.csv` and start making calls! 📞
