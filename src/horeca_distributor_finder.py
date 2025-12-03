"""
HORECA Frozen Poultry Distributor Finder
=========================================
End-to-end pipeline:
1. Google Maps Text Search API (scraping)
2. Deduplication (fuzzy matching + normalization)
3. AI Classification via LLM (OpenAI/Gemini)
4. Export final prospect list

Author: Quan Dinh
Date: 2025-12-02
"""

import os
from dotenv import load_dotenv
from typing import List, Dict

# Import reusable modules
try:
    # When running from root as python src/script.py
    from src.google_maps_scraper import GoogleMapsScraper
    from src.ai_classifier import AIClassifier
    from src.utils import Deduplicator, FileManager
except ImportError:
    # When running from src as python script.py
    from google_maps_scraper import GoogleMapsScraper
    from ai_classifier import AIClassifier
    from utils import Deduplicator, FileManager

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for scraping, deduplication, and classification"""

    # API Keys
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY_HERE")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Optional: for LLM classification

    # File paths
    BASE_DIR = "."
    RAW_LEADS_FILE = "1_raw_leads.csv"
    DEDUPED_LEADS_FILE = "2_deduped_leads.csv"
    CLASSIFIED_LEADS_FILE = "3_classified_leads.csv"
    FINAL_PROSPECTS_FILE = "FINAL_HORECA_PROSPECTS.csv"

    @classmethod
    def set_output_dir(cls, output_dir: str = None):
        """Set output directory for files"""
        if output_dir:
            # Create base directory: {output_dir}/base
            cls.BASE_DIR = os.path.join(output_dir, "base")
            os.makedirs(cls.BASE_DIR, exist_ok=True)
            print(f"📂 Output directory set to: {cls.BASE_DIR}")
        else:
            cls.BASE_DIR = "."
            
        cls.RAW_LEADS_FILE = os.path.join(cls.BASE_DIR, "1_raw_leads.csv")
        cls.DEDUPED_LEADS_FILE = os.path.join(cls.BASE_DIR, "2_deduped_leads.csv")
        cls.CLASSIFIED_LEADS_FILE = os.path.join(cls.BASE_DIR, "3_classified_leads.csv")
        cls.FINAL_PROSPECTS_FILE = os.path.join(cls.BASE_DIR, "FINAL_HORECA_PROSPECTS.csv")

    # Deduplication thresholds
    FUZZY_MATCH_THRESHOLD = 85  # 0-100 for company name similarity

    # Classification
    ENABLE_AI_CLASSIFICATION = False  # Default to False, enable via flag
    BATCH_SIZE = 10  # Number of records to classify in one API call


# ============================================================================
# LOCATION DATA & SEARCH QUERIES
# ============================================================================

try:
    from search_config_horeca import SEARCH_LOCATIONS, SEARCH_QUERIES
except ImportError:
    # Fallback or error handling if file is missing (though it should be there)
    print("⚠️  Warning: src/search_config_horeca.py not found. Using empty configuration.")
    SEARCH_LOCATIONS = {}
    SEARCH_QUERIES = {}


# ============================================================================
# PROMPT GENERATOR
# ============================================================================

def generate_horeca_prompt(records: List[Dict]) -> str:
    """Generate classification prompt for HORECA distributors"""
    
    prompt = """
You are a B2B foodservice analyst. Analyze these businesses and determine if they are a good fit for selling frozen crispy duck/chicken to Asian restaurants (Vietnamese/Chinese) in HORECA (Hotel/Restaurant/Catering) channel.

Records to analyze:
"""
    for i, record in enumerate(records):
        prompt += f"""
        --- Record {i+1} ---
        ID: {record.get('id', 'N/A')}
        Company Name: {record.get('company_name', 'Unknown')}
        Address: {record.get('full_address', 'Unknown')}
        Website: {record.get('website', 'N/A')}
        Phone: {record.get('phone', 'N/A')}
        Business Types: {record.get('types', 'N/A')}
        """

    prompt += """
    For EACH record, return a JSON object with these fields:
    1. record_index (int): The record number (1, 2, 3...) matching the input.
    2. is_horeca_distributor (true/false): Does this appear to supply restaurants/catering/foodservice?
    3. is_ethnic_asian (true/false): Is this Vietnamese, Chinese, or pan-Asian food focused?
    4. likely_frozen_poultry (true/false): Does it likely stock frozen poultry (duck/chicken)?
    5. priority_score (1-10): Overall fit score (10 = perfect fit, 1 = unlikely fit)
    6. contact_recommendation (text): Brief recommendation on contacting this company

    Return ONLY a valid JSON ARRAY containing objects for all records. No markdown formatting.
    Example:
    [
    {"record_index": 1, "is_horeca_distributor": true, ...},
    {"record_index": 2, "is_horeca_distributor": false, ...}
    ]
    """
    return prompt


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """Run the complete pipeline"""
    import argparse

    parser = argparse.ArgumentParser(description="HORECA Distributor Finder")
    parser.add_argument("output_dir", nargs="?", help="Optional output directory name")
    parser.add_argument("--resume", action="store_true", help="Skip scraping/deduping and resume from existing deduped file")
    parser.add_argument("--ai-classify", action="store_true", help="Enable AI classification (disabled by default)")
    args = parser.parse_args()

    # Set output directory if provided
    Config.set_output_dir(args.output_dir)
    
    # Override AI setting
    if args.ai_classify:
        Config.ENABLE_AI_CLASSIFICATION = True

    print("\n" + "🚀 "*35)
    print("HORECA FROZEN POULTRY DISTRIBUTOR FINDER")
    print("End-to-End Pipeline")
    print("🚀 "*35)

    # Check for API key
    if Config.GOOGLE_MAPS_API_KEY == "YOUR_API_KEY_HERE":
        print("\n❌ ERROR: Google Maps API key not configured!")
        print("   Please set GOOGLE_MAPS_API_KEY environment variable or in config.")
        return

    raw_leads = []
    deduped_leads = []

    if args.resume:
        print("\n⏩ RESUMING (Skipping Scraping & Deduplication)")
        
        if not os.path.exists(Config.DEDUPED_LEADS_FILE):
            print(f"\n❌ ERROR: Deduped leads file not found: {Config.DEDUPED_LEADS_FILE}")
            print("   Cannot resume. Please run without --resume first.")
            return

        deduped_leads = FileManager.load_csv(Config.DEDUPED_LEADS_FILE)
        
    else:
        # ========== PHASE 1: SCRAPING ==========
        scraper = GoogleMapsScraper(Config.GOOGLE_MAPS_API_KEY)
        
        print("\n" + "="*70)
        print("PHASE 1: GOOGLE MAPS SCRAPING")
        print("="*70)

        for country, tiers in SEARCH_LOCATIONS.items():
            print(f"\n🌍 {country}")

            all_locations = (
                tiers.get("tier_1", []) +
                tiers.get("tier_2", []) +
                tiers.get("tier_3", [])
            )

            queries = SEARCH_QUERIES.get(country, [])

            for location in all_locations:
                print(f"  📍 {location['name']} ({location['radius']}km radius)")

                for query in queries:
                    print(f"    🔍 {query}...", end=" ", flush=True)

                    results = scraper.search_text(
                        query=query,
                        lat=location["lat"],
                        lng=location["lng"],
                        radius=location["radius"]
                    )

                    raw_leads.extend(results)
                    print(f"({len(results)} found)")

        print(f"\n✅ Total API calls: {scraper.call_count}")
        print(f"✅ Total results: {scraper.total_results}")

        # Save raw leads
        FileManager.save_csv(raw_leads, Config.RAW_LEADS_FILE)

        # ========== PHASE 2: DEDUPLICATION ==========
        deduped_leads = Deduplicator.deduplicate(raw_leads, Config.FUZZY_MATCH_THRESHOLD)

        # Save deduped leads
        FileManager.save_csv(deduped_leads, Config.DEDUPED_LEADS_FILE)

    # ========== PHASE 3: AI CLASSIFICATION (OPTIONAL) ==========
    if Config.ENABLE_AI_CLASSIFICATION:
        classifier = AIClassifier(Config.OPENAI_API_KEY)
        classified_leads = classifier.classify_all(
            records=deduped_leads,
            prompt_generator=generate_horeca_prompt,
            output_file=Config.CLASSIFIED_LEADS_FILE,
            batch_size=Config.BATCH_SIZE,
            resume=True
        )
        
        # Filter to high-priority leads
        final_leads = [
            r for r in classified_leads
            if r.get("priority_score") and float(r.get("priority_score", 0)) >= 7
        ]
        final_leads = sorted(
            final_leads,
            key=lambda x: float(x.get("priority_score", 0)),
            reverse=True
        )
    else:
        final_leads = deduped_leads

    # Save final prospects
    FileManager.save_csv(final_leads, Config.FINAL_PROSPECTS_FILE)

    # Generate report
    FileManager.generate_report(final_leads)

    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE!")
    print("="*70)
    print(f"\nOutput files:")
    if not args.resume:
        print(f"  1. {Config.RAW_LEADS_FILE} (raw scraping results)")
        print(f"  2. {Config.DEDUPED_LEADS_FILE} (after deduplication)")
    
    if Config.ENABLE_AI_CLASSIFICATION:
        print(f"  3. {Config.CLASSIFIED_LEADS_FILE} (after AI classification)")
    print(f"  4. {Config.FINAL_PROSPECTS_FILE} (final prospects - MAIN FILE)")
    print("\n")


if __name__ == "__main__":
    main()
