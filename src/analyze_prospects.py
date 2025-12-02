"""
HORECA Distributor Finder - Data Analysis Helper
==================================================

After running the main script, use this to analyze and filter results.
"""

import csv
import json
from collections import defaultdict, Counter
from typing import List, Dict

class ProspectAnalyzer:
    """Analyze HORECA prospects from CSV"""

    def __init__(self, csv_file: str):
        self.records = self._load_csv(csv_file)

    @staticmethod
    def _load_csv(filepath: str) -> List[Dict]:
        """Load CSV records"""
        records = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)
        return records

    def summary(self):
        """Print summary statistics"""
        print("\n" + "="*70)
        print("PROSPECT SUMMARY")
        print("="*70)

        print(f"\nTotal prospects: {len(self.records)}")

        # Extract country from full_address
        countries = defaultdict(int)
        cities = defaultdict(int)

        for r in self.records:
            address = r.get("full_address", "")
            if address:
                # Last part of address is usually country
                parts = address.split(",")
                if len(parts) > 1:
                    city = parts[-2].strip() if len(parts) > 1 else ""
                    country = parts[-1].strip() if len(parts) > 0 else ""
                    cities[city] += 1
                    countries[country] += 1

        print("\nBy country:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(self.records)) * 100
            print(f"  {country}: {count} ({pct:.1f}%)")

        print("\nTop 10 cities:")
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {city}: {count}")

        # Websites
        with_website = sum(1 for r in self.records if r.get("website"))
        print(f"\nWith website: {with_website} ({(with_website/len(self.records)*100):.1f}%)")

        # Phone numbers
        with_phone = sum(1 for r in self.records if r.get("phone"))
        print(f"With phone: {with_phone} ({(with_phone/len(self.records)*100):.1f}%)")

        # Ratings
        with_rating = [float(r.get("rating", 0)) for r in self.records if r.get("rating")]
        if with_rating:
            avg_rating = sum(with_rating) / len(with_rating)
            print(f"\nAverage rating: {avg_rating:.2f}⭐")
            print(f"Rating range: {min(with_rating):.1f} - {max(with_rating):.1f}⭐")

    def filter_by_rating(self, min_rating: float = 4.0) -> List[Dict]:
        """Filter prospects by minimum rating"""
        filtered = [
            r for r in self.records 
            if r.get("rating") and float(r.get("rating", 0)) >= min_rating
        ]
        print(f"\n✅ Filtered to {len(filtered)} prospects with rating >= {min_rating}⭐")
        return filtered

    def filter_by_country(self, country_keyword: str) -> List[Dict]:
        """Filter by country"""
        filtered = [
            r for r in self.records 
            if country_keyword.lower() in r.get("full_address", "").lower()
        ]
        print(f"\n✅ Filtered to {len(filtered)} prospects in {country_keyword}")
        return filtered

    def filter_by_contact_info(self, require_phone: bool = False, require_website: bool = False) -> List[Dict]:
        """Filter by availability of contact info"""
        filtered = self.records

        if require_phone:
            filtered = [r for r in filtered if r.get("phone")]
            print(f"✅ Filtered to {len(filtered)} with phone number")

        if require_website:
            filtered = [r for r in filtered if r.get("website")]
            print(f"✅ Filtered to {len(filtered)} with website")

        return filtered

    def top_prospects(self, limit: int = 20) -> List[Dict]:
        """Get top prospects by rating"""
        sorted_records = sorted(
            [r for r in self.records if r.get("rating")],
            key=lambda x: float(x.get("rating", 0)),
            reverse=True
        )

        print(f"\nTop {limit} prospects by rating:")
        print("-" * 70)

        for i, r in enumerate(sorted_records[:limit], 1):
            name = r.get("company_name", "Unknown")
            rating = r.get("rating", "N/A")
            reviews = r.get("review_count", "0")
            city = r.get("city", "Unknown")
            phone = r.get("phone", "")

            print(f"{i:2d}. {name} ({city})")
            print(f"    Rating: {rating}⭐ ({reviews} reviews)")
            print(f"    Phone: {phone}")
            print()

        return sorted_records[:limit]

    def export_filtered(self, records: List[Dict], output_file: str):
        """Export filtered records to CSV"""
        if not records:
            print("⚠️  No records to export")
            return

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = list(records[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"✅ Exported {len(records)} records to {output_file}")

    def search_by_name(self, keyword: str) -> List[Dict]:
        """Search prospects by company name"""
        results = [
            r for r in self.records 
            if keyword.lower() in r.get("company_name", "").lower()
        ]

        print(f"\n🔍 Found {len(results)} results for '{keyword}':")
        for r in results[:10]:  # Show top 10
            print(f"  • {r.get('company_name', 'Unknown')} ({r.get('city', 'Unknown')})")

        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more")

        return results


def main():
    """Interactive analysis tool"""

    import os
    import argparse

    parser = argparse.ArgumentParser(description="HORECA Prospect Analysis Tool")
    parser.add_argument("output_dir", nargs="?", help="Optional output directory name")
    args = parser.parse_args()

    # Determine file paths and search for input CSV
    potential_paths = []
    
    if args.output_dir:
        # If directory provided, prioritize structure inside it
        potential_paths.append(os.path.join(args.output_dir, "base", "FINAL_HORECA_PROSPECTS.csv"))
        potential_paths.append(os.path.join(args.output_dir, "FINAL_HORECA_PROSPECTS.csv"))
        
        # Set output directory
        output_dir = os.path.join(args.output_dir, "output")
        print(f"📂 Target directory: {args.output_dir}")
    else:
        # Default to current directory
        potential_paths.append("FINAL_HORECA_PROSPECTS.csv")
        potential_paths.append(os.path.join("base", "FINAL_HORECA_PROSPECTS.csv"))
        
        output_dir = "."

    # Find first existing file
    csv_file = None
    for path in potential_paths:
        if os.path.exists(path):
            csv_file = path
            break

    if not csv_file:
        print(f"❌ Input file 'FINAL_HORECA_PROSPECTS.csv' not found.")
        print(f"   Checked locations:")
        for p in potential_paths:
            print(f"   - {p}")
        print("\nPlease run 'horeca_distributor_finder.py' first to generate data.")
        return

    # Create output directory if it doesn't exist (only if we have a valid input)
    if args.output_dir:
        os.makedirs(output_dir, exist_ok=True)
        print(f"📂 Saving output to: {output_dir}")

    print(f"✅ Found input file: {csv_file}")

    print("\n" + "🔍 "*35)
    print("HORECA PROSPECT ANALYSIS TOOL")
    print("🔍 "*35)

    analyzer = ProspectAnalyzer(csv_file)
    analyzer.summary()

    print("\n" + "="*70)
    print("ANALYSIS OPTIONS")
    print("="*70)
    print("\n1. Top 20 prospects (by rating)")
    print("2. Filter by country (Germany/Spain/France)")
    print("3. Filter by minimum rating (e.g., 4.0+)")
    print("4. Prospects with phone number")
    print("5. Prospects with website")
    print("6. Search by company name")
    print("0. Exit")

    while True:
        choice = input("\nSelect option (0-6): ").strip()

        if choice == "0":
            print("\n👋 Goodbye!")
            break

        elif choice == "1":
            top = analyzer.top_prospects(20)

            save = input("\nExport to CSV? (y/n): ").strip().lower()
            if save == "y":
                filename = "filtered_top20.csv"
                filepath = os.path.join(output_dir, filename)
                analyzer.export_filtered(top, filepath)

        elif choice == "2":
            country = input("Enter country (Germany/Spain/France): ").strip()
            filtered = analyzer.filter_by_country(country)

            save = input("Export to CSV? (y/n): ").strip().lower()
            if save == "y":
                filename = f"filtered_{country}.csv"
                filepath = os.path.join(output_dir, filename)
                analyzer.export_filtered(filtered, filepath)

        elif choice == "3":
            rating = float(input("Minimum rating (e.g., 4.0): ").strip())
            filtered = analyzer.filter_by_rating(rating)

            save = input("Export to CSV? (y/n): ").strip().lower()
            if save == "y":
                filename = f"filtered_rating{rating}.csv"
                filepath = os.path.join(output_dir, filename)
                analyzer.export_filtered(filtered, filepath)

        elif choice == "4":
            filtered = analyzer.filter_by_contact_info(require_phone=True)

            save = input("Export to CSV? (y/n): ").strip().lower()
            if save == "y":
                filename = "filtered_with_phone.csv"
                filepath = os.path.join(output_dir, filename)
                analyzer.export_filtered(filtered, filepath)

        elif choice == "5":
            filtered = analyzer.filter_by_contact_info(require_website=True)

            save = input("Export to CSV? (y/n): ").strip().lower()
            if save == "y":
                filename = "filtered_with_website.csv"
                filepath = os.path.join(output_dir, filename)
                analyzer.export_filtered(filtered, filepath)

        elif choice == "6":
            keyword = input("Enter company name or keyword: ").strip()
            analyzer.search_by_name(keyword)

        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
