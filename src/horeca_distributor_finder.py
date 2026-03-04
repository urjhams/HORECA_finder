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
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # For AI classification (Gemini)
    # Legacy support for OpenAI key name
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # File paths
    BASE_DIR = "."
    RAW_LEADS_FILE = "1_raw_restaurants.csv"
    DEDUPED_LEADS_FILE = "2_deduped_restaurants.csv"
    CLASSIFIED_LEADS_FILE = "3_classified_restaurants.csv"
    FINAL_PROSPECTS_FILE = "FINAL_RESTAURANT_PROSPECTS.csv"

    @classmethod
    def set_output_dir(cls, output_dir: str | None = None):
        """Set output directory for files"""
        if output_dir:
            # Create base directory: {output_dir}/base
            cls.BASE_DIR = os.path.join(output_dir, "base")
            os.makedirs(cls.BASE_DIR, exist_ok=True)
            print(f"📂 Output directory set to: {cls.BASE_DIR}")
        else:
            cls.BASE_DIR = "."
            
        cls.RAW_LEADS_FILE = os.path.join(cls.BASE_DIR, "1_raw_restaurants.csv")
        cls.DEDUPED_LEADS_FILE = os.path.join(cls.BASE_DIR, "2_deduped_restaurants.csv")
        cls.CLASSIFIED_LEADS_FILE = os.path.join(cls.BASE_DIR, "3_classified_restaurants.csv")
        cls.FINAL_PROSPECTS_FILE = os.path.join(cls.BASE_DIR, "FINAL_RESTAURANT_PROSPECTS.csv")

    # Deduplication thresholds
    FUZZY_MATCH_THRESHOLD = 85  # 0-100 for company name similarity

    # Classification
    ENABLE_AI_CLASSIFICATION: bool = False  # Default to False, enable via flag
    BATCH_SIZE = 40  # Number of records to classify in one API call (optimized for restaurants)


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

Focus on small-to-medium restaurants, bistros, and quick-service establishments that need hand towels and paper boxes for takeaway/delivery.

Records to analyze:
"""
    for i, record in enumerate(records):
        prompt += f"""
{i+1}. {record.get('company_name', 'Unknown')} | {record.get('city', '')} | Types: {record.get('types', 'N/A')}"""

    prompt += """

For EACH record, return a JSON object with these fields:
1. record_index (int): The record number (1, 2, 3...)
2. restaurant_type (string): "Chinese", "Vietnamese", "Turkish", "Other", or "Not a Restaurant"
3. business_model (string): "bistro", "quick-service", "gastronomy", "fine-dining", "cafe", "other", or "unknown"
4. is_target_customer (true/false): Good prospect for hand towels and paper boxes?
5. product_fit_score (1-10): Likelihood to buy supplies (10 = high takeaway volume, 1 = unlikely)
6. reasoning (text): Brief explanation (1 sentence)
7. contact_recommendation (text): "High priority", "Medium priority", "Low priority", or "Skip"

Classification Guidelines:
- Bistros/quick-service/döner: High priority (more takeaway = more packaging)
- Fine-dining: Low priority (less takeaway)
- Look for keywords: bistro, imbiss, schnellimbiss, döner, pho, dim sum, asia, china, vietnam, türk

Return ONLY a valid JSON ARRAY. No markdown.
Example:
[
{"record_index": 1, "restaurant_type": "Vietnamese", "business_model": "bistro", "is_target_customer": true, "product_fit_score": 8, "reasoning": "Vietnamese bistro likely has high takeaway volume", "contact_recommendation": "High priority"},
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
        scraper = GoogleMapsScraper(Config.GOOGLE_MAPS_API_KEY)
        
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
        classifier = AIClassifier(Config.GEMINI_API_KEY)
        classified_leads = classifier.classify_all(
            records=deduped_leads,
            prompt_generator=generate_restaurant_classification_prompt,
            output_file=Config.CLASSIFIED_LEADS_FILE,
            batch_size=Config.BATCH_SIZE,
            resume=True
        )
        
        # ========== PHASE 4: FINAL FILTERING & EXPORT BY TYPE ==========
        print("\n" + "="*70)
        print("PHASE 4: FINAL FILTERING & EXPORT")
        print("="*70)
        
        # Filter to target restaurants with good product fit
        target_restaurants = [
            r for r in classified_leads
            if (r.get("is_target_customer") == True or r.get("is_target_customer") == "true")
            and r.get("product_fit_score") and float(r.get("product_fit_score", 0)) >= 5
            and r.get("phone")  # Must have phone number for outreach
        ]
        
        print(f"\n📊 Total classified: {len(classified_leads)}")
        print(f"📊 Target restaurants (score ≥5 + has phone): {len(target_restaurants)}")
        
        # Sort by product fit score
        target_restaurants = sorted(
            target_restaurants,
            key=lambda x: float(x.get("product_fit_score", 0)),
            reverse=True
        )
        
        # Group by restaurant type
        by_type = {
            "Chinese": [],
            "Vietnamese": [],
            "Turkish": [],
            "Other": []
        }
        
        for r in target_restaurants:
            rtype = r.get("restaurant_type", "Other")
            if rtype in by_type:
                by_type[rtype].append(r)
            else:
                by_type["Other"].append(r)
        
        # Save separate files for each type
        print("\n📁 Exporting by restaurant type:")
        
        chinese_file = os.path.join(Config.BASE_DIR, "FINAL_CHINESE_RESTAURANTS.csv")
        vietnamese_file = os.path.join(Config.BASE_DIR, "FINAL_VIETNAMESE_RESTAURANTS.csv")
        turkish_file = os.path.join(Config.BASE_DIR, "FINAL_TURKISH_RESTAURANTS.csv")
        other_file = os.path.join(Config.BASE_DIR, "FINAL_OTHER_RESTAURANTS.csv")
        
        if by_type["Chinese"]:
            FileManager.save_csv(by_type["Chinese"], chinese_file)
        else:
            print(f"  ⚠️  No Chinese restaurants to export")
        
        if by_type["Vietnamese"]:
            FileManager.save_csv(by_type["Vietnamese"], vietnamese_file)
        else:
            print(f"  ⚠️  No Vietnamese restaurants to export")
        
        if by_type["Turkish"]:
            FileManager.save_csv(by_type["Turkish"], turkish_file)
        else:
            print(f"  ⚠️  No Turkish restaurants to export")
        
        if by_type["Other"]:
            FileManager.save_csv(by_type["Other"], other_file)
        else:
            print(f"  ℹ️  No 'Other' restaurants to export")
        
        # Save combined file (all target restaurants)
        final_leads = target_restaurants
        
    else:
        # No classification - just use deduped leads
        final_leads = deduped_leads

    # Save final prospects (combined)
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
        print(f"\n  📁 By Restaurant Type:")
        if os.path.exists(os.path.join(Config.BASE_DIR, "FINAL_CHINESE_RESTAURANTS.csv")):
            print(f"     🥡 FINAL_CHINESE_RESTAURANTS.csv ({len(by_type.get('Chinese', []))} restaurants)")
        if os.path.exists(os.path.join(Config.BASE_DIR, "FINAL_VIETNAMESE_RESTAURANTS.csv")):
            print(f"     🍜 FINAL_VIETNAMESE_RESTAURANTS.csv ({len(by_type.get('Vietnamese', []))} restaurants)")
        if os.path.exists(os.path.join(Config.BASE_DIR, "FINAL_TURKISH_RESTAURANTS.csv")):
            print(f"     🥙 FINAL_TURKISH_RESTAURANTS.csv ({len(by_type.get('Turkish', []))} restaurants)")
        if os.path.exists(os.path.join(Config.BASE_DIR, "FINAL_OTHER_RESTAURANTS.csv")):
            print(f"     🍽️  FINAL_OTHER_RESTAURANTS.csv ({len(by_type.get('Other', []))} restaurants)")
    
    print(f"\n  4. {Config.FINAL_PROSPECTS_FILE} (all target restaurants - MAIN FILE)")
    print("\n")


if __name__ == "__main__":
    main()
