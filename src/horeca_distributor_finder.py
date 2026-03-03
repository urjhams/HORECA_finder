"""
Germany Restaurant Finder for B2B Supplies
===========================================
End-to-end pipeline:
1. Google Maps Text Search API (scraping restaurants across Germany)
2. Deduplication (fuzzy matching + normalization)
3. AI Classification via LLM (Gemini) - categorize by restaurant type
4. Export final prospect list (Chinese, Vietnamese, Turkish restaurants)

Target: Small-medium restaurants, bistros needing hand towels and paper boxes

Author: Quan Dinh
Date: 2026-03-03
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

    # Email extraction
    ENABLE_EMAIL_EXTRACTION = True  # Enable website email scraping

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

def generate_restaurant_classification_prompt(records: List[Dict]) -> str:
    """Generate classification prompt for restaurant categorization"""
    
    prompt = """
You are a B2B sales analyst specializing in restaurant supplies. Analyze these businesses and classify them by restaurant type to determine if they are good prospects for selling hand towels and paper boxes (disposable packaging supplies).

Target Customers:
- Chinese restaurants (bistros, quick-service, gastronomy)
- Vietnamese restaurants (bistros, quick-service, gastronomy)  
- Turkish restaurants (döner shops, bistros, quick-service, gastronomy)

Focus on small-to-medium restaurants, bistros, and quick-service establishments that need:
- Hand towels (paper towels for customers/kitchen)
- Paper boxes (takeaway packaging, food containers)

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
        Rating: {record.get('rating', 'N/A')}
        Reviews: {record.get('review_count', 'N/A')}
        """

    prompt += """
    For EACH record, return a JSON object with these fields:
    1. record_index (int): The record number (1, 2, 3...) matching the input.
    2. restaurant_type (string): One of: "Chinese", "Vietnamese", "Turkish", "Other", "Not a Restaurant"
    3. business_model (string): One of: "bistro", "quick-service", "gastronomy", "fine-dining", "cafe", "other", "unknown"
    4. is_target_customer (true/false): Is this a good prospect for hand towels and paper boxes?
    5. product_fit_score (1-10): Likelihood to buy supplies (10 = very high need for takeaway packaging, 1 = unlikely)
    6. reasoning (text): Brief explanation of classification (mention business type, likely volume, takeaway focus)
    7. contact_recommendation (text): Recommendation on contacting this restaurant

    Classification Guidelines:
    - Bistros and quick-service restaurants: Higher priority (more takeaway orders = more packaging needs)
    - Fine-dining: Lower priority (less takeaway, premium packaging preferences)
    - Cafes/Bakeries: Medium priority if they serve food
    - Look for keywords: bistro, imbiss, schnellimbiss, döner, pho, dim sum, takeaway, delivery
    - Rate higher if they have good reviews (active business = more orders)

    Return ONLY a valid JSON ARRAY containing objects for all records. No markdown formatting.
    Example:
    [
    {"record_index": 1, "restaurant_type": "Vietnamese", "business_model": "bistro", "is_target_customer": true, "product_fit_score": 8, "reasoning": "Vietnamese bistro with takeaway focus", "contact_recommendation": "High priority - call directly"},
    {"record_index": 2, "restaurant_type": "Other", "business_model": "unknown", "is_target_customer": false, "product_fit_score": 2, "reasoning": "Not a target restaurant type", "contact_recommendation": "Skip"}
    ]
    """
    return prompt


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """Run the complete pipeline"""
    import argparse

    parser = argparse.ArgumentParser(description="Germany Restaurant Finder - B2B Supplies")
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
    print("GERMANY RESTAURANT FINDER - B2B SUPPLIES")
    print("Find Chinese, Vietnamese & Turkish Restaurants")
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
        scraper = GoogleMapsScraper(
            Config.GOOGLE_MAPS_API_KEY,
            enable_email_extraction=Config.ENABLE_EMAIL_EXTRACTION
        )
        
        print("\n" + "="*70)
        print("PHASE 1: GOOGLE MAPS SCRAPING")
        print("="*70)

        for country, tiers in SEARCH_LOCATIONS.items():
            print(f"\n🌍 {country}")

            all_locations = (
                tiers.get("tier_1_mega", []) +
                tiers.get("tier_2_large", []) +
                tiers.get("tier_3_regional", []) +
                tiers.get("tier_4_gaps", []) +
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

                    # Extract emails from websites if enabled
                    if Config.ENABLE_EMAIL_EXTRACTION and results:
                        results = scraper.enrich_with_emails(results)

                    raw_leads.extend(results)
                    print(f"({len(results)} found)")

        print(f"\n✅ Total API calls: {scraper.call_count}")
        print(f"✅ Total results: {scraper.total_results}")
        if Config.ENABLE_EMAIL_EXTRACTION:
            print(f"✅ Emails extracted: {scraper.email_extraction_count}")

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
            prompt_generator=generate_restaurant_classification_prompt,
            output_file=Config.CLASSIFIED_LEADS_FILE,
            batch_size=Config.BATCH_SIZE,
            resume=True
        )
        
        # Filter to target restaurants with good product fit
        final_leads = [
            r for r in classified_leads
            if (r.get("is_target_customer") == True or r.get("is_target_customer") == "true")
            and r.get("product_fit_score") and float(r.get("product_fit_score", 0)) >= 5
        ]
        final_leads = sorted(
            final_leads,
            key=lambda x: float(x.get("product_fit_score", 0)),
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
