"""
Utility classes for Restaurant Finder
"""

import csv
from typing import List, Dict
from fuzzywuzzy import fuzz

class Deduplicator:
    """Remove duplicates and normalize restaurant data"""

    @staticmethod
    def normalize_company_name(name: str) -> str:
        """Normalize company name for comparison"""
        import re
        name = name.lower().strip()
        name = re.sub(r"\s+", " ", name)  # Remove extra spaces
        # Remove common legal entities and restaurant keywords
        name = re.sub(r"(gmbh|ltd|inc|ag|sa|srl|sas|s\.a\.r\.l|eurl)$", "", name)
        name = re.sub(r"(restaurant|bistro|imbiss|café|cafe)$", "", name)
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
        """Check if two names are likely the same restaurant"""
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

        # Same website → likely duplicate (unless it's a chain website)
        if record1.get("website") and record2.get("website"):
            if record1["website"] == record2["website"]:
                # Check if different cities - could be chain with same website
                if record1.get("city") and record2.get("city"):
                    if record1["city"].lower() != record2["city"].lower():
                        return False  # Different cities, probably chain branches
                return True

        # Same phone → likely duplicate
        if record1.get("phone") and record2.get("phone"):
            phone1 = Deduplicator.normalize_phone(record1["phone"])
            phone2 = Deduplicator.normalize_phone(record2["phone"])
            if phone1 and phone2 and phone1 == phone2:
                return True

        # Fuzzy match on name + same city (restaurants with same name in different cities are different)
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
    def deduplicate(records: List[Dict], threshold: int = 85) -> List[Dict]:
        """Remove duplicates from restaurant records"""
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
                    threshold
                ):
                    seen_indices.add(j)

        print(f"📊 Output: {len(unique_records)} unique records")
        print(f"🗑️  Duplicates removed: {len(records) - len(unique_records)}")

        return unique_records


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
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
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
        """Generate summary report for restaurants"""

        print("\n" + "="*70)
        print("FINAL SUMMARY REPORT - RESTAURANT PROSPECTS")
        print("="*70)

        print(f"\n📊 Total restaurants: {len(records)}")

        # Count by city
        by_city = {}
        for r in records:
            city = r.get("city", "Unknown")
            if city not in by_city:
                by_city[city] = 0
            by_city[city] += 1

        print("\n🏙️  By City (Top 10):")
        for city, count in sorted(by_city.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {city}: {count}")

        # Count by restaurant type (if classified)
        if records and "restaurant_type" in records[0]:
            by_type = {}
            for r in records:
                rtype = r.get("restaurant_type", "Unknown")
                if rtype not in by_type:
                    by_type[rtype] = 0
                by_type[rtype] += 1

            print("\n🍜 By Restaurant Type:")
            for rtype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                print(f"  {rtype}: {count}")

        # Count with contact info
        with_phone = sum(1 for r in records if r.get("phone"))
        with_website = sum(1 for r in records if r.get("website"))

        print("\n📞 Contact Information:")
        print(f"  With phone: {with_phone} ({with_phone/len(records)*100:.1f}%)")
        print(f"  With website: {with_website} ({with_website/len(records)*100:.1f}%)")

        # Top product fit scores (if classified)
        if records and "product_fit_score" in records[0]:
            top_scores = sorted(
                [r for r in records if r.get("product_fit_score")],
                key=lambda x: float(x.get("product_fit_score", 0)),
                reverse=True
            )[:10]

            if top_scores:
                print("\n⭐ Top 10 Prospects (by product fit score):")
                for i, r in enumerate(top_scores, 1):
                    score = r.get("product_fit_score", "N/A")
                    rtype = r.get("restaurant_type", "Unknown")
                    model = r.get("business_model", "unknown")
                    print(f"  {i}. {r.get('company_name', 'Unknown')} ({r.get('city', 'Unknown')}) - {rtype} {model} - Score: {score}/10")
