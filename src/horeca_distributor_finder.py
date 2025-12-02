
"""
HORECA Frozen Poultry Distributor Finder
=========================================
End-to-end pipeline:
1. Google Maps Text Search API (scraping)
2. Deduplication (fuzzy matching + normalization)
3. AI Classification via LLM (OpenAI/Gemini)
4. Export final prospect list

Author: Your Name
Date: 2025-12-02
"""

import requests
import csv
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os
from dotenv import load_dotenv

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

    # Google Maps API settings
    GOOGLE_MAPS_BASE_URL = "https://places.googleapis.com/v1/places:searchText"
    RATE_LIMIT_DELAY = 1.0  # seconds between requests
    JITTER_RANGE = (0, 0.5)  # random delay variance

    # Pagination
    MAX_PAGES_PER_QUERY = 3  # 20 results per page, so 3 = 60 results max

    # File paths
    RAW_LEADS_FILE = "1_raw_leads.csv"
    DEDUPED_LEADS_FILE = "2_deduped_leads.csv"
    CLASSIFIED_LEADS_FILE = "3_classified_leads.csv"
    FINAL_PROSPECTS_FILE = "FINAL_HORECA_PROSPECTS.csv"

    # Deduplication thresholds
    FUZZY_MATCH_THRESHOLD = 85  # 0-100 for company name similarity

    # Classification
    ENABLE_AI_CLASSIFICATION = False  # Set to True if you have OpenAI key


# ============================================================================
# LOCATION DATA: 28 cities across 3 countries with tiered radius
# ============================================================================

SEARCH_LOCATIONS = {
    "Germany": {
        "tier_1": [  # 30 km radius (mega cities)
            {"name": "Berlin", "lat": 52.52, "lng": 13.40, "radius": 30},
            {"name": "Hamburg", "lat": 53.55, "lng": 10.00, "radius": 30},
            {"name": "Munich", "lat": 48.14, "lng": 11.58, "radius": 30},
            {"name": "Cologne", "lat": 50.94, "lng": 6.96, "radius": 30},
        ],
        "tier_2": [  # 25 km radius (large cities)
            {"name": "Frankfurt", "lat": 50.11, "lng": 8.68, "radius": 25},
            {"name": "Stuttgart", "lat": 48.78, "lng": 9.18, "radius": 25},
            {"name": "Düsseldorf", "lat": 51.22, "lng": 6.78, "radius": 25},
            {"name": "Leipzig", "lat": 51.34, "lng": 12.37, "radius": 25},
        ],
        "tier_3": [  # 20 km radius (medium cities)
            {"name": "Nuremberg", "lat": 49.45, "lng": 11.08, "radius": 20},
            {"name": "Hanover", "lat": 52.37, "lng": 9.73, "radius": 20},
            {"name": "Bremen", "lat": 53.07, "lng": 8.81, "radius": 20},
        ]
    },
    "Spain": {
        "tier_1": [  # 30 km radius
            {"name": "Barcelona", "lat": 41.39, "lng": 2.17, "radius": 30},
            {"name": "Madrid", "lat": 40.42, "lng": -3.70, "radius": 30},
        ],
        "tier_2": [  # 25 km radius
            {"name": "Valencia", "lat": 39.47, "lng": -0.38, "radius": 25},
            {"name": "Seville", "lat": 37.39, "lng": -5.98, "radius": 25},
            {"name": "Bilbao", "lat": 43.26, "lng": -2.92, "radius": 25},
        ],
        "tier_3": [  # 20 km radius
            {"name": "Malaga", "lat": 36.72, "lng": -4.42, "radius": 20},
            {"name": "Palma", "lat": 39.57, "lng": 2.65, "radius": 20},
            {"name": "Zaragoza", "lat": 41.65, "lng": -0.88, "radius": 20},
        ]
    },
    "France": {
        "tier_1": [  # 30 km radius
            {"name": "Paris", "lat": 48.86, "lng": 2.35, "radius": 30},
            {"name": "Lyon", "lat": 45.76, "lng": 4.84, "radius": 30},
        ],
        "tier_2": [  # 25 km radius
            {"name": "Marseille", "lat": 43.30, "lng": 5.37, "radius": 25},
            {"name": "Toulouse", "lat": 43.60, "lng": 1.44, "radius": 25},
        ],
        "tier_3": [  # 20 km radius
            {"name": "Nice", "lat": 43.70, "lng": 7.26, "radius": 20},
            {"name": "Bordeaux", "lat": 44.84, "lng": -0.58, "radius": 20},
            {"name": "Lille", "lat": 50.63, "lng": 3.06, "radius": 20},
            {"name": "Strasbourg", "lat": 48.58, "lng": 7.75, "radius": 20},
            {"name": "Nantes", "lat": 47.22, "lng": -1.55, "radius": 20},
        ]
    }
}

# Search queries per country (localized)
SEARCH_QUERIES = {
    "Germany": [
        "Vietnamesische Lebensmittel Großhandel",
        "Chinesischer Lebensmittel Großhandel",
        "Asiatischer Tiefkühlkost Großhandel HORECA",
        "Frozen duck importer HORECA",
    ],
    "Spain": [
        "Distribuidor comida vietnamita",
        "Importador alimentos chinos congelados",
        "Mayorista comida asiática HORECA",
        "Frozen poultry distributor",
    ],
    "France": [
        "Grossiste alimentation vietnamienne",
        "Distributeur aliments chinois surgelés",
        "Fournisseur restaurant asiatique HORECA",
        "Distributeur volaille surgelée",
    ]
}


# ============================================================================
# PHASE 1: GOOGLE MAPS SCRAPING
# ============================================================================

class GoogleMapsScraper:
    """Scrape HORECA distributors from Google Maps API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.GOOGLE_MAPS_BASE_URL
        self.call_count = 0
        self.total_results = 0
        self.session = requests.Session()

    def search_text(self, query: str, lat: float, lng: float, radius: int) -> List[Dict]:
        """
        Perform a text search on Google Maps API (New Places API v1)

        Args:
            query: Search query string
            lat: Latitude of bias location
            lng: Longitude of bias location
            radius: Search radius in kilometers (converted to meters for API)

        Returns:
            List of place results with metadata
        """
        results = []
        page_token = None
        page_count = 0

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json",
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.internationalPhoneNumber,places.addressComponents,places.location,places.rating,places.userRatingCount,places.priceLevel,places.types,nextPageToken"
        }

        while page_count < Config.MAX_PAGES_PER_QUERY:
            # Add jitter to avoid rate limiting
            delay = Config.RATE_LIMIT_DELAY + random.uniform(*Config.JITTER_RANGE)
            time.sleep(delay)

            # Build request payload
            payload = {
                "textQuery": query,
                "locationBias": {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lng},
                        "radius": radius * 1000.0  # Convert km to meters (ensure float)
                    }
                },
                "maxResultCount": 20
            }

            if page_token:
                payload["pageToken"] = page_token

            # Make request
            try:
                response = self.session.post(self.base_url, headers=headers, json=payload, timeout=10)
                
                # Check for errors and print details if any
                if response.status_code != 200:
                    print(f"    ❌ Error: {response.status_code} {response.reason}")
                    print(f"    ❌ Response: {response.text}")
                
                response.raise_for_status()
                data = response.json()

                self.call_count += 1

                # Extract results
                if "places" in data:
                    for place in data["places"]:
                        result = self._parse_place(place, query)
                        results.append(result)
                        self.total_results += 1

                # Check for next page
                page_token = data.get("nextPageToken")
                page_count += 1

                if not page_token:
                    break

            except requests.RequestException as e:
                print(f"    ❌ Error: {str(e)}")
                break

        return results

    def _parse_place(self, place: Dict, query: str) -> Dict:
        """Extract and normalize place data"""

        # Extract address components
        formatted_address = place.get("formattedAddress", "")
        
        # Parse address components for postal code and city
        postal_code = ""
        city = ""
        street = ""
        
        # Try to extract from address components (more reliable)
        comps = place.get("addressComponents", [])
        for c in comps:
            types = c.get("types", [])
            if "postal_code" in types:
                postal_code = c.get("longText", "") or c.get("text", "")
            elif "locality" in types:
                city = c.get("longText", "") or c.get("text", "")
            elif "route" in types:
                street = c.get("longText", "") or c.get("text", "")
        
        # Fallback to string splitting if components fail
        if not city or not postal_code:
            address_parts = formatted_address.split(",")
            if not street and len(address_parts) > 0:
                street = address_parts[0].strip()
            if not city and len(address_parts) > 1:
                city = address_parts[1].strip()
            if not postal_code and len(address_parts) > 2:
                postal_code = address_parts[2].strip()

        return {
            "id": place.get("id"),
            "company_name": place.get("displayName", {}).get("text", ""),
            "street_address": street,
            "city": city,
            "postal_code": postal_code,
            "full_address": formatted_address,
            "latitude": place.get("location", {}).get("latitude"),
            "longitude": place.get("location", {}).get("longitude"),
            "phone": place.get("internationalPhoneNumber", ""),
            "website": place.get("websiteUri", ""),
            "rating": place.get("rating"),
            "review_count": place.get("userRatingCount", 0),
            "types": ",".join(place.get("types", [])),
            "source": "google_maps_textsearch",
            "search_query": query,
            "scrape_timestamp": datetime.now().isoformat(),
        }

    def run_all_searches(self) -> List[Dict]:
        """Run all searches across all countries and cities"""
        all_results = []

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

                    results = self.search_text(
                        query=query,
                        lat=location["lat"],
                        lng=location["lng"],
                        radius=location["radius"]
                    )

                    all_results.extend(results)
                    print(f"({len(results)} found)")

        print(f"\n✅ Total API calls: {self.call_count}")
        print(f"✅ Total results: {self.total_results}")

        return all_results


# ============================================================================
# PHASE 2: DEDUPLICATION & NORMALIZATION
# ============================================================================

class Deduplicator:
    """Remove duplicates and normalize data"""

    @staticmethod
    def normalize_company_name(name: str) -> str:
        """Normalize company name for comparison"""
        import re
        name = name.lower().strip()
        name = re.sub(r"\s+", " ", name)  # Remove extra spaces
        name = re.sub(r"(gmbh|ltd|inc|ag|sa|srl|sas|s\.a\.r\.l|eurl)$", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number for comparison"""
        import re
        phone = re.sub(r"\D", "", phone)  # Remove non-digits
        return phone[-9:]  # Last 9 digits

    @staticmethod
    def fuzzy_match_names(name1: str, name2: str, threshold: int = 85) -> bool:
        """Check if two names are likely the same company"""
        norm1 = Deduplicator.normalize_company_name(name1)
        norm2 = Deduplicator.normalize_company_name(name2)

        similarity = fuzz.token_set_ratio(norm1, norm2)
        return similarity >= threshold

    @staticmethod
    def is_duplicate(record1: Dict, record2: Dict, threshold: int = 85) -> bool:
        """Determine if two records are duplicates"""

        # Same place_id → definitely duplicate
        if record1.get("id") and record2.get("id"):
            if record1["id"] == record2["id"]:
                return True

        # Same website → likely duplicate
        if record1.get("website") and record2.get("website"):
            if record1["website"] == record2["website"]:
                return True

        # Same phone → likely duplicate
        if record1.get("phone") and record2.get("phone"):
            phone1 = Deduplicator.normalize_phone(record1["phone"])
            phone2 = Deduplicator.normalize_phone(record2["phone"])
            if phone1 and phone2 and phone1 == phone2:
                return True

        # Fuzzy match on name + same city
        if record1.get("city") and record2.get("city"):
            if record1["city"].lower() == record2["city"].lower():
                if Deduplicator.fuzzy_match_names(
                    record1["company_name"],
                    record2["company_name"],
                    threshold
                ):
                    return True

        return False

    @staticmethod
    def deduplicate(records: List[Dict]) -> List[Dict]:
        """Remove duplicates from records"""
        unique_records = []
        seen_indices = set()

        print("\n" + "="*70)
        print("PHASE 2: DEDUPLICATION & NORMALIZATION")
        print("="*70)

        print(f"\n📊 Input: {len(records)} records")

        for i, record1 in enumerate(records):
            if i in seen_indices:
                continue

            # Keep this record
            unique_records.append(record1)
            seen_indices.add(i)

            # Mark similar records as duplicates
            for j in range(i + 1, len(records)):
                if j in seen_indices:
                    continue

                record2 = records[j]

                if Deduplicator.is_duplicate(
                    record1,
                    record2,
                    Config.FUZZY_MATCH_THRESHOLD
                ):
                    seen_indices.add(j)

        print(f"📊 Output: {len(unique_records)} unique records")
        print(f"🗑️  Duplicates removed: {len(records) - len(unique_records)}")

        return unique_records


# ============================================================================
# PHASE 3: AI CLASSIFICATION (OPTIONAL)
# ============================================================================

class AIClassifier:
    """Classify leads using LLM (OpenAI or similar)"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.call_count = 0

    @staticmethod
    def generate_prompt(record: Dict) -> str:
        """Generate classification prompt for a record"""

        prompt = f"""
You are a B2B foodservice analyst. Analyze this business and determine if it's a good fit for selling frozen crispy duck/chicken to Asian restaurants (Vietnamese/Chinese) in HORECA (Hotel/Restaurant/Catering) channel.

Company Name: {record.get('company_name', 'Unknown')}
Address: {record.get('full_address', 'Unknown')}
Website: {record.get('website', 'N/A')}
Phone: {record.get('phone', 'N/A')}
Business Types: {record.get('types', 'N/A')}

Based on available information, classify:

1. is_horeca_distributor (true/false): Does this appear to supply restaurants/catering/foodservice?
2. is_ethnic_asian (true/false): Is this Vietnamese, Chinese, or pan-Asian food focused?
3. likely_frozen_poultry (true/false): Does it likely stock frozen poultry (duck/chicken)?
4. priority_score (1-10): Overall fit score (10 = perfect fit, 1 = unlikely fit)
5. contact_recommendation (text): Brief recommendation on contacting this company

Return ONLY valid JSON, no markdown:
{{
  "is_horeca_distributor": bool,
  "is_ethnic_asian": bool,
  "likely_frozen_poultry": bool,
  "priority_score": int,
  "contact_recommendation": "text"
}}
"""
        return prompt

    def classify_record(self, record: Dict) -> Dict:
        """Classify a single record using LLM"""

        if not self.api_key:
            print("⚠️  No OpenAI API key configured. Skipping AI classification.")
            return {
                "is_horeca_distributor": None,
                "is_ethnic_asian": None,
                "likely_frozen_poultry": None,
                "priority_score": 5,
                "contact_recommendation": "Requires manual review"
            }

        try:
            import openai
            openai.api_key = self.api_key

            prompt = self.generate_prompt(record)

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a B2B foodservice analyst. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )

            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            self.call_count += 1

            return result

        except Exception as e:
            print(f"    ❌ Classification error: {str(e)}")
            return {
                "is_horeca_distributor": None,
                "is_ethnic_asian": None,
                "likely_frozen_poultry": None,
                "priority_score": 5,
                "contact_recommendation": "Error during classification"
            }

    def classify_all(self, records: List[Dict]) -> List[Dict]:
        """Classify all records"""

        if not Config.ENABLE_AI_CLASSIFICATION:
            print("\n⏭️  AI classification disabled. Skipping...")
            return records

        print("\n" + "="*70)
        print("PHASE 3: AI CLASSIFICATION")
        print("="*70)

        for i, record in enumerate(records):
            print(f"\n  Classifying {i+1}/{len(records)}: {record['company_name']}", end=" ... ", flush=True)

            classification = self.classify_record(record)
            record.update(classification)

            print(f"Score: {classification.get('priority_score', 'N/A')}/10")

            # Rate limit: 3-4 requests per minute to avoid API throttling
            time.sleep(20)

        print(f"\n✅ Total classifications: {self.call_count}")

        return records


# ============================================================================
# FILE I/O
# ============================================================================

class FileManager:
    """Handle CSV import/export"""

    @staticmethod
    def save_csv(records: List[Dict], filepath: str):
        """Save records to CSV"""
        if not records:
            print(f"⚠️  No records to save")
            return

        fieldnames = list(records[0].keys())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"✅ Saved {len(records)} records to {filepath}")

    @staticmethod
    def load_csv(filepath: str) -> List[Dict]:
        """Load records from CSV"""
        records = []

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)

        print(f"✅ Loaded {len(records)} records from {filepath}")

        return records

    @staticmethod
    def generate_report(records: List[Dict]):
        """Generate summary report"""

        print("\n" + "="*70)
        print("FINAL SUMMARY REPORT")
        print("="*70)

        print(f"\nTotal prospects: {len(records)}")

        # Group by country
        by_country = {}
        for r in records:
            country = r.get("city", "Unknown").split(",")[-1].strip() if "," in r.get("city", "") else "Unknown"
            if country not in by_country:
                by_country[country] = 0
            by_country[country] += 1

        print("\nBy country:")
        for country, count in sorted(by_country.items(), key=lambda x: x[1], reverse=True):
            print(f"  {country}: {count}")

        # Top priority scores
        if "priority_score" in records[0]:
            top_scores = sorted(
                [r for r in records if "priority_score" in r and r["priority_score"]],
                key=lambda x: float(x["priority_score"]),
                reverse=True
            )[:5]

            if top_scores:
                print("\nTop 5 prospects:")
                for i, r in enumerate(top_scores, 1):
                    score = r.get("priority_score", "N/A")
                    print(f"  {i}. {r['company_name']} ({r['city']}) - Score: {score}/10")


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """Run the complete pipeline"""

    print("\n" + "🚀 "*35)
    print("HORECA FROZEN POULTRY DISTRIBUTOR FINDER")
    print("End-to-End Pipeline")
    print("🚀 "*35)

    # Check for API key
    if Config.GOOGLE_MAPS_API_KEY == "YOUR_API_KEY_HERE":
        print("\n❌ ERROR: Google Maps API key not configured!")
        print("   Please set GOOGLE_MAPS_API_KEY environment variable or in config.")
        return

    # ========== PHASE 1: SCRAPING ==========
    scraper = GoogleMapsScraper(Config.GOOGLE_MAPS_API_KEY)
    raw_leads = scraper.run_all_searches()

    # Save raw leads
    FileManager.save_csv(raw_leads, Config.RAW_LEADS_FILE)

    # ========== PHASE 2: DEDUPLICATION ==========
    deduped_leads = Deduplicator.deduplicate(raw_leads)

    # Save deduped leads
    FileManager.save_csv(deduped_leads, Config.DEDUPED_LEADS_FILE)

    # ========== PHASE 3: AI CLASSIFICATION (OPTIONAL) ==========
    if Config.ENABLE_AI_CLASSIFICATION:
        classifier = AIClassifier()
        classified_leads = classifier.classify_all(deduped_leads)
        FileManager.save_csv(classified_leads, Config.CLASSIFIED_LEADS_FILE)

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
    print(f"  1. {Config.RAW_LEADS_FILE} (raw scraping results)")
    print(f"  2. {Config.DEDUPED_LEADS_FILE} (after deduplication)")
    if Config.ENABLE_AI_CLASSIFICATION:
        print(f"  3. {Config.CLASSIFIED_LEADS_FILE} (after AI classification)")
    print(f"  4. {Config.FINAL_PROSPECTS_FILE} (final prospects - MAIN FILE)")
    print("\n")


if __name__ == "__main__":
    main()
