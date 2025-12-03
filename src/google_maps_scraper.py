"""
Google Maps Scraper Module
"""

import requests
import time
import random
from datetime import datetime
from typing import List, Dict

class GoogleMapsScraper:
    """Scrape HORECA distributors from Google Maps API"""

    def __init__(self, api_key: str, base_url: str = "https://places.googleapis.com/v1/places:searchText", 
                 rate_limit_delay: float = 1.0, jitter_range: tuple = (0, 0.5), max_pages: int = 3):
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.jitter_range = jitter_range
        self.max_pages = max_pages
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

        while page_count < self.max_pages:
            # Add jitter to avoid rate limiting
            delay = self.rate_limit_delay + random.uniform(*self.jitter_range)
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
