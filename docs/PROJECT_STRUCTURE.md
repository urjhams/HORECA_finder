# PROJECT STRUCTURE & IMPLEMENTATION GUIDE

## 📦 Files Created

You now have a complete, production-ready system:

```
horeca_finder/
│
├── horeca_distributor_finder.py      ⭐ MAIN SCRIPT (355 lines)
│   ├── Phase 1: Google Maps Scraping
│   ├── Phase 2: Deduplication
│   └── Phase 3: AI Classification (optional)
│
├── analyze_prospects.py               🔍 ANALYSIS TOOL
│   ├── Interactive filtering
│   ├── Export utilities
│   └── Summary statistics
│
├── requirements.txt                   📦 DEPENDENCIES
├── .env.template                      🔐 CONFIG TEMPLATE
├── README.md                          📖 FULL DOCUMENTATION
├── QUICK_START.md                     ⚡ 5-MINUTE SETUP
└── PROJECT_STRUCTURE.md               📋 THIS FILE

Output files (generated after running):
├── 1_raw_leads.csv
├── 2_deduped_leads.csv
├── 3_classified_leads.csv (optional)
└── FINAL_HORECA_PROSPECTS.csv ⭐ MAIN RESULT
```

---

## 🚀 QUICK SETUP (Copy & Paste)

### Step 1: Install packages
```bash
pip install -r requirements.txt
```

### Step 2: Configure Google Maps API
```bash
cp .env.template .env
# Edit .env, add your Google Maps API key
```

### Step 3: Run the scraper
```bash
python horeca_distributor_finder.py
```

### Step 4: Analyze results
```bash
python analyze_prospects.py
```

---

## 📊 EXPECTED RESULTS

### Scraping Phase (2-3 minutes)
- **28 cities** across Germany, Spain, France
- **4 search queries per country** (Vietnamese, Chinese, Asian, Frozen poultry)
- **2 pages per query** = 60 results max per query
- **Total API calls:** ~224 calls
- **Expected raw results:** 2,200-3,200 companies

### After Deduplication
- **Removes branch duplicates:** ~30-40% reduction
- **Normalizes company names, phone numbers**
- **Expected final:** 1,500-2,000 unique companies

### Final Prospect List
- Clean CSV with:
  - Company name
  - Street address
  - City / Postal code
  - Phone number
  - Website URL
  - Google rating
  - Review count
- **Ready for cold outreach!**

---

## 🛠️ TECHNICAL DETAILS

### Architecture

```
Input Layer (Data Sources)
    ↓
Google Maps API
    ↓
Google Maps Scraper (Phase 1)
    ├─ Text Search API calls
    ├─ Rate limiting (1 sec/request)
    ├─ Pagination (up to 60 results/query)
    └─ JSON parsing & normalization
    ↓
Raw CSV (2,200-3,200 records)
    ↓
Deduplicator (Phase 2)
    ├─ Fuzzy name matching (FuzzyWuzzy)
    ├─ Phone number normalization
    ├─ Website/Place ID matching
    └─ Duplicate removal logic
    ↓
Deduplicated CSV (1,500-2,000 unique records)
    ↓
AI Classifier (Phase 3 - Optional)
    ├─ OpenAI GPT-4 API calls
    ├─ Classification prompts
    ├─ Priority scoring (1-10)
    └─ Contact recommendations
    ↓
Final Prospects CSV (500-1,000 high-quality leads)
    ↓
Output Layer (Ready for Outreach)
```

### Key Classes & Functions

**GoogleMapsScraper**
- `search_text()` - Execute single API request
- `_parse_place()` - Extract place data
- `run_all_searches()` - Orchestrate all searches

**Deduplicator**
- `normalize_company_name()` - Clean names
- `fuzzy_match_names()` - Compare similarity
- `is_duplicate()` - Detect duplicate records
- `deduplicate()` - Main deduplication logic

**AIClassifier** (optional)
- `generate_prompt()` - Create LLM prompt
- `classify_record()` - Single record classification
- `classify_all()` - Batch classification

**FileManager**
- `save_csv()` - Write CSV files
- `load_csv()` - Read CSV files
- `generate_report()` - Summary statistics

**ProspectAnalyzer** (analyze_prospects.py)
- `summary()` - Overview statistics
- `filter_by_rating()` - Filter by quality
- `filter_by_country()` - Geographic filter
- `top_prospects()` - Ranked list
- `export_filtered()` - Save to CSV

---

## 💰 COST BREAKDOWN

| Component | Unit | Count | Cost |
|-----------|------|-------|------|
| Google Maps Text Search | $0.0145/query | 224 | $3.25 |
| (with pagination) | | | |
| OpenAI GPT-4 classification | $0.001-0.003/call | 1,500 | $15-45 |
| **Total (without AI)** | | | **$3-5** |
| **Total (with AI)** | | | **$20-50** |

**Google gives $200/month free** → This is completely free for first month

---

## 📈 WORKFLOW TIMELINE

### Day 1 (Setup - 30 minutes)
- ✅ Get Google Maps API key
- ✅ Install Python packages
- ✅ Configure .env file
- ✅ Test script

### Day 1-2 (Execution - 5 minutes runtime + review)
- ✅ Run `horeca_distributor_finder.py`
- ✅ Wait for scraping/deduplication (~3 minutes)
- ✅ Review output CSV
- ✅ Run `analyze_prospects.py` to filter

### Day 2-3 (Outreach Prep - 1-2 hours)
- ✅ Identify top 20-30 prospects
- ✅ Research companies online
- ✅ Prepare pitch/email
- ✅ Create contact list

### Week 1-2 (Outreach - Ongoing)
- ✅ Make phone calls
- ✅ Send emails with samples
- ✅ Track responses
- ✅ Follow up

---

## 🔍 EXAMPLE USAGE SCENARIOS

### Scenario 1: Find all German distributors with 4.5+ rating
```python
analyzer = ProspectAnalyzer("FINAL_HORECA_PROSPECTS.csv")
filtered = analyzer.filter_by_country("Germany")
filtered = [r for r in filtered if float(r.get("rating", 0)) >= 4.5]
analyzer.export_filtered(filtered, "germany_top_rated.csv")
```

### Scenario 2: Get only companies with phone & website
```python
analyzer = ProspectAnalyzer("FINAL_HORECA_PROSPECTS.csv")
filtered = analyzer.filter_by_contact_info(
    require_phone=True,
    require_website=True
)
analyzer.export_filtered(filtered, "contacted_ready.csv")
```

### Scenario 3: Search for specific company
```python
analyzer = ProspectAnalyzer("FINAL_HORECA_PROSPECTS.csv")
results = analyzer.search_by_name("Euro Asia")
# Shows: Euro Asia Union, Hamburg, +49401234567, etc.
```

---

## 🔧 CUSTOMIZATION OPTIONS

### Change Search Queries

In `horeca_distributor_finder.py`, edit `SEARCH_QUERIES`:

```python
SEARCH_QUERIES = {
    "Germany": [
        "Your custom query 1",
        "Your custom query 2",
        "Your custom query 3",
    ],
    # ...
}
```

### Add More Cities

Edit `SEARCH_LOCATIONS`:

```python
"Germany": {
    "tier_1": [
        {"name": "Berlin", "lat": 52.52, "lng": 13.40, "radius": 30},
        {"name": "YOUR_CITY", "lat": XX.XX, "lng": XX.XX, "radius": 30},
    ]
}
```

Get coordinates from: https://maps.google.com/ (right-click → copy coordinates)

### Adjust Deduplication Sensitivity

```python
# In Config class
FUZZY_MATCH_THRESHOLD = 85  # 0-100, higher = stricter matching
```

### Enable AI Classification

1. Get OpenAI API key: https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-your-key-here`
3. In script, set: `ENABLE_AI_CLASSIFICATION = True`

---

## 🐛 DEBUGGING & TROUBLESHOOTING

### Script doesn't find API key
```bash
# Check .env exists and has correct content
cat .env
echo $GOOGLE_MAPS_API_KEY  # Should print your key
```

### "Zero results" for a city
- Search term might be too specific
- Smaller cities may have fewer businesses
- Try broader keywords or different cities

### Script running slowly
- This is normal (1 second delay between API calls for rate limiting)
- 224 calls × 1 sec = ~224 seconds = 3-4 minutes
- You can reduce `RATE_LIMIT_DELAY` to 0.5 sec (risky)

### Getting "quota exceeded"
- Check Google Cloud Console → check billing
- Verify API has quota available
- Check if you hit daily limits (usually 25,000 requests/day)

---

## 📱 AFTER YOU GET THE LIST

### Cold Calling Script

```
"Hi, we're [Your Company], importing high-quality frozen crispy duck and chicken 
from [Country]. I noticed [Distributor Name] supplies restaurants in the area. 
Would your procurement team be interested in samples? 

Our products are:
- Fresh frozen (IQF)
- Certified for EU import
- Competitive pricing
- Minimum order: [X kg]

Can I send you a brochure?"
```

### Email Template

```
Subject: Fresh Frozen Duck/Chicken - HORECA Distribution Partnership

Hi [Procurement Manager],

We're [Your Company], a direct importer of premium frozen poultry for 
Asian restaurants and catering.

I found your company on Google Maps and see you supply restaurants 
in the [City] area. Your excellent 4.5★ rating shows you take quality 
seriously.

We offer:
✓ Fresh frozen crispy duck (whole, portioned)
✓ Marinated chicken (Vietnamese style)
✓ IQF poultry ready for wok cooking
✓ EU food safety certified
✓ Competitive wholesale pricing

Would you be open to a product sample? I can arrange delivery this week.

Best regards,
[Your Name]
[Your Company]
[Phone] | [Email]
```

---

## 📊 METRICS & KPIs

Track your outreach performance:

| Metric | Target | Formula |
|--------|--------|---------|
| Response Rate | 10-15% | Responses / Total Contacted |
| Sample Request Rate | 20-30% | Samples Ordered / Contacted |
| Order Close Rate | 5-10% | Orders / Samples Sent |
| Average Order Value | $5,000+ | Total Revenue / Total Orders |

Example:
- Contacted: 100 distributors
- Responses: 12 (12%)
- Sample requests: 4 (33%)
- Orders: 1 ($8,000) - after 2-4 weeks

---

## ✅ NEXT STEPS CHECKLIST

- [ ] Install Python 3.8+
- [ ] Get Google Maps API key
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure .env file
- [ ] Run main script: `python horeca_distributor_finder.py`
- [ ] Open `FINAL_HORECA_PROSPECTS.csv`
- [ ] Analyze with: `python analyze_prospects.py`
- [ ] Filter for top 20-30 prospects
- [ ] Research companies online
- [ ] Prepare pitch/email template
- [ ] Start cold calling / outreach
- [ ] Track responses
- [ ] Ship samples to interested parties
- [ ] Close deals 🎉

---

## 📞 SUPPORT RESOURCES

- Google Maps API: https://developers.google.com/maps/documentation/places
- OpenAI API: https://platform.openai.com/docs/guides/gpt
- FuzzyWuzzy: https://github.com/seatgeek/fuzzywuzzy
- Python requests: https://requests.readthedocs.io/
- Stack Overflow: https://stackoverflow.com/ (search your error)

---

## 💡 TIPS FOR SUCCESS

1. **Start with German distributors first** - Largest market
2. **Call during business hours** (9-12 AM or 2-5 PM local time)
3. **Prepare samples beforehand** - Don't promise without inventory
4. **Build relationships** - This is B2B, long-term partnerships matter
5. **Follow up** - Most deals require 2-3 follow-ups
6. **Track everything** - Use a CRM or spreadsheet to track leads
7. **Ask for referrals** - "Who else should I talk to?" is gold
8. **Attend trade shows** - European frozen food shows in March/October
9. **Join industry groups** - EFCO (European Frozen Food Council)
10. **Keep data clean** - Dedup and verify before big outreach campaigns

---

## 🎯 SUCCESS STORY EXAMPLE

**Scenario:** Import frozen crispy duck from Vietnam

1. **Week 1:** Run scraper → 1,847 unique prospects across 3 countries
2. **Week 1:** Analyze → Filter to 94 with 4.0+ rating in Germany
3. **Week 2:** Call 20 prospects → 2 interested in samples (10% response)
4. **Week 3:** Send samples to 2 companies
5. **Week 4:** Follow up → 1 wants to order (50% close)
6. **Month 2:** First order 500kg @ €15/kg = €7,500
7. **Month 3:** Relationship established, repeat orders every 2 weeks
8. **Month 6:** €45,000+ revenue from single distributor partnership

---

## 📝 FINAL NOTES

- This script respects **Google Maps ToS** (public data only)
- **GDPR compliant** (no personal data, business data only)
- **B2B outreach is legal** (not spam if business-relevant)
- **Cost-effective** (~$3-5 for thousands of leads)
- **Fully automated** (runs in 3-5 minutes)
- **Highly customizable** (change queries, cities, thresholds)
- **Production-ready** (error handling, logging, cleanup)

---

**Good luck with your HORECA expansion! 🚀**

Questions? Check README.md or revisit the code comments.
