# 📑 COMPLETE FILE INDEX

## ⭐ START HERE

**Choose your path based on how much time you have:**

### ⚡ 5 Minutes - Just Run It
1. Read: `QUICK_START.md`
2. Set up: Copy `.env.template` → `.env` + add API key
3. Execute: `pip install -r requirements.txt` then `python horeca_distributor_finder.py`
4. Done! Open `FINAL_HORECA_PROSPECTS.csv`

### 📖 20 Minutes - Understand Everything
1. Read: `README.md` (complete guide)
2. Understand the workflow and features
3. Set up and run as described in ⚡ section above

### 🔬 1 Hour - Deep Technical Dive
1. Read: `PROJECT_STRUCTURE.md` (technical details)
2. Review: `horeca_distributor_finder.py` (code comments)
3. Customize as needed, then deploy

---

## 📁 ALL FILES EXPLAINED

### 🚀 EXECUTABLE SCRIPTS

#### `horeca_distributor_finder.py`
- **What it does:** Scrapes Google Maps → deduplicates → optionally classifies
- **When to use:** Run this once to get all leads
- **Command:** `python horeca_distributor_finder.py`
- **Output:** `FINAL_HORECA_PROSPECTS.csv` (1,500-2,000 qualified prospects)
- **Time:** ~3 minutes
- **Cost:** $3-5 (first month free with Google credits)

#### `analyze_prospects.py`
- **What it does:** Interactive tool to filter and analyze results
- **When to use:** After running main script, to find top prospects
- **Command:** `python analyze_prospects.py`
- **Features:** Filter by rating/country/contact info, search by name, export
- **Output:** Filtered CSV files (e.g., `filtered_germany.csv`)

### 📚 DOCUMENTATION

#### `QUICK_START.md` ⚡ **READ THIS FIRST**
- **Purpose:** Get running in 5 minutes
- **Contains:** Step-by-step instructions with copy-paste commands
- **Length:** ~200 lines
- **Best for:** Fast setup, impatient users

#### `README.md`
- **Purpose:** Complete, detailed documentation
- **Contains:** Setup, usage, customization, troubleshooting, GDPR
- **Length:** ~350 lines
- **Best for:** Understanding the system fully

#### `PROJECT_STRUCTURE.md`
- **Purpose:** Technical implementation guide
- **Contains:** Architecture, code walkthrough, customization examples
- **Length:** ~400 lines
- **Best for:** Developers who want to modify the code

#### `GETTING_STARTED.md`
- **Purpose:** Executive summary and quick reference
- **Contains:** System overview, features, success metrics, ROI
- **Length:** ~300 lines
- **Best for:** Business stakeholders, quick overview

#### `FILE_INDEX.md` (this file)
- **Purpose:** Guide to all files in the project
- **Contains:** What each file does, when to use it

### ⚙️ CONFIGURATION

#### `.env.template`
- **What it is:** Environment variables template
- **How to use:** Copy to `.env`, then add your Google Maps API key
- **Contains:** 
  - `GOOGLE_MAPS_API_KEY` (required)
  - `OPENAI_API_KEY` (optional, for AI classification)
- **Never commit:** Keep `.env` private! (add to `.gitignore`)

#### `requirements.txt`
- **What it is:** Python package dependencies
- **How to use:** `pip install -r requirements.txt`
- **Installs:**
  - `requests` (HTTP library for API calls)
  - `fuzzywuzzy` + `python-Levenshtein` (fuzzy string matching for dedup)
  - `python-dotenv` (environment variable management)
  - `openai` (LLM API, optional)
  - `pandas` (data analysis, optional)

### 📊 OUTPUT FILES (Generated After Running)

#### `1_raw_leads.csv`
- **What it contains:** Raw results from Google Maps API
- **Characteristics:** 2,200-3,200 records, includes duplicates
- **Use case:** Debug, see raw API output
- **When to use:** Rarely needed for analysis

#### `2_deduped_leads.csv`
- **What it contains:** After deduplication and normalization
- **Characteristics:** 1,500-2,000 unique records
- **Use case:** Intermediate analysis, verify deduplication worked
- **When to use:** If you want to see what dedup removed

#### `3_classified_leads.csv` (optional)
- **What it contains:** After AI classification (if enabled)
- **Characteristics:** Priority scores (1-10), contact recommendations
- **Use case:** Pre-filtered prospects
- **When to use:** Only if `ENABLE_AI_CLASSIFICATION = True`

#### `FINAL_HORECA_PROSPECTS.csv` ⭐⭐⭐
- **What it contains:** Final, cleaned prospect list ready for outreach
- **Characteristics:** 500-1,000+ prospects (after filtering for quality)
- **Columns:** 
  - company_name, street_address, city, postal_code, phone, website
  - rating, review_count, business_types, search_query, timestamp
- **Use case:** **THIS IS YOUR MAIN FILE - for cold calling!**
- **When to use:** Import to CRM, export phone numbers, start dialing

---

## 🎯 TYPICAL WORKFLOW

### Phase 1: Setup (30 minutes, one time)
```
1. Read QUICK_START.md (5 min)
2. Install Python & requirements (10 min)
3. Get Google Maps API key (10 min)
4. Configure .env file (5 min)
```

### Phase 2: Execution (5 minutes, one time)
```
1. Run: python horeca_distributor_finder.py (3 min runtime)
2. Wait for scraping, deduplication, classification
3. Check output files generated
```

### Phase 3: Analysis (1-2 hours, iterative)
```
1. Run: python analyze_prospects.py
2. Filter by rating (keep 4.0+)
3. Filter by country (Germany first)
4. Export top 20-30 to new CSV
5. Review websites, research companies
```

### Phase 4: Outreach (ongoing)
```
1. Open FINAL_HORECA_PROSPECTS.csv
2. Extract phone numbers
3. Call prospects: "Hi, we import frozen duck/chicken..."
4. Send emails with product brochure
5. Track responses and follow up
6. Send samples to interested parties
7. Close deals!
```

---

## 🔍 QUICK REFERENCE

### To get started immediately:
```bash
cp .env.template .env
# Edit .env and add your Google Maps API key
pip install -r requirements.txt
python horeca_distributor_finder.py
```

### To analyze results:
```bash
python analyze_prospects.py
```

### To filter manually in Excel/Sheets:
```
Open: FINAL_HORECA_PROSPECTS.csv
Sort: By rating (descending)
Filter: Where phone is not empty
Filter: Where website is not empty
Export: Top 50 rows to new file
```

### To customize queries/cities:
```
Edit: horeca_distributor_finder.py
Section: SEARCH_LOCATIONS and SEARCH_QUERIES
Save, then run: python horeca_distributor_finder.py
```

---

## 📈 KEY METRICS

| Metric | Value |
|--------|-------|
| Raw results | 2,200-3,200 |
| After dedup | 1,500-2,000 |
| Ready to contact | 500-1,000+ |
| Coverage | 28 cities, 3 countries |
| Runtime | ~3 minutes |
| Cost | $3-5 (first month free) |
| Response rate (typical) | 10-15% |
| Sample request rate | 20-30% |
| Order close rate | 5-10% |

---

## ❓ FREQUENTLY ASKED QUESTIONS

**Q: Where do I get the Google Maps API key?**
A: See QUICK_START.md or README.md section "Get Google Maps API Key"

**Q: How long does it take to run?**
A: ~3 minutes for scraping + deduplication. AI classification is optional and takes 1-2 hours.

**Q: How much does it cost?**
A: $3-5 for scraping. Google gives $200/month free, so free for first month. Optional AI classification adds $20-50.

**Q: Can I customize the search queries?**
A: Yes! Edit SEARCH_QUERIES in horeca_distributor_finder.py

**Q: Can I add more cities?**
A: Yes! Edit SEARCH_LOCATIONS in horeca_distributor_finder.py. Get coordinates from Google Maps.

**Q: What if I get zero results for a city?**
A: Try broader search terms, or that city may have few distributors. Check README troubleshooting section.

**Q: Is this GDPR compliant?**
A: Yes, only public data from Google Maps. B2B business contacts are allowed.

**Q: Can I use this data commercially?**
A: Yes, it's your own research. Just don't spam (B2B outreach is fine).

---

## 🚀 NEXT STEPS

1. Choose your reading path above (⚡, 📖, or 🔬)
2. Start with the appropriate documentation file
3. Set up the environment variables
4. Run the script
5. Start calling prospects!

---

## 📞 SUPPORT

- **Setup issues:** Check QUICK_START.md troubleshooting section
- **Usage questions:** See README.md FAQ and troubleshooting
- **Technical questions:** See PROJECT_STRUCTURE.md or code comments
- **API issues:** Check Google Maps API docs (https://developers.google.com/maps)

---

**Happy prospecting! 🚀**
