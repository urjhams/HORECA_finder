"""
Utility classes for HORECA Finder
"""

import csv
from typing import List, Dict
from fuzzywuzzy import fuzz

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
    def deduplicate(records: List[Dict], threshold: int = 85) -> List[Dict]:
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
        """Generate summary report"""

        print("\n" + "="*70)
        print("FINAL SUMMARY REPORT")
        print("="*70)

        print(f"\nTotal prospects: {len(records)}")

        # Group by city/country logic can be handled generically or by caller, 
        # but for now we'll keep the simple city/country extraction
        by_location = {}
        for r in records:
            # Try to guess country from city string if it has it, else just city
            loc = r.get("city", "Unknown")
            if "," in loc:
                loc = loc.split(",")[-1].strip()
            
            if loc not in by_location:
                by_location[loc] = 0
            by_location[loc] += 1

        print("\nBy Location:")
        for loc, count in sorted(by_location.items(), key=lambda x: x[1], reverse=True):
            print(f"  {loc}: {count}")

        # Top priority scores
        if records and "priority_score" in records[0]:
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
