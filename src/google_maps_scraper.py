"""
Google Maps Scraper Module
"""

import requests
import time
import random
import re
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class GoogleMapsScraper:
    """Scrape restaurants from Google Maps API with email extraction"""

    def __init__(self, api_key: str, base_url: str = "https://places.googleapis.com/v1/places:searchText", 
                 rate_limit_delay: float = 1.0, jitter_range: tuple = (0, 0.5), max_pages: int = 3,
                 enable_email_extraction: bool = True):
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.jitter_range = jitter_range
        self.max_pages = max_pages
        self.enable_email_extraction = enable_email_extraction
        self.call_count = 0
        self.total_results = 0
        self.email_extraction_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

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

            # Convert radius (km) to approximate lat/lng offset for bounding box
            # 1 degree latitude ≈ 111 km, 1 degree longitude ≈ 111 km * cos(lat)
            import math
            lat_offset = radius / 111.0
            lng_offset = radius / (111.0 * math.cos(math.radians(lat)))
            
            # Build request payload with rectangle (required for locationRestriction)
            payload = {
                "textQuery": query,
                "locationRestriction": {
                    "rectangle": {
                        "low": {
                            "latitude": lat - lat_offset,
                            "longitude": lng - lng_offset
                        },
                        "high": {
                            "latitude": lat + lat_offset,
                            "longitude": lng + lng_offset
                        }
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
            "email": "",  # Will be populated by extract_email_from_website if enabled
            "rating": place.get("rating"),
            "review_count": place.get("userRatingCount", 0),
            "types": ",".join(place.get("types", [])),
            "source": "google_maps_textsearch",
            "search_query": query,
            "scrape_timestamp": datetime.now().isoformat(),
        }

    def extract_email_from_website(self, website_url: str) -> Optional[str]:
        """
        Extract email address from a website
        
        Args:
            website_url: URL of the website to scrape
            
        Returns:
            Email address if found, None otherwise
        """
        if not website_url or website_url == "N/A":
            return None
        
        try:
            # Add delay to avoid being blocked
            time.sleep(random.uniform(0.5, 1.5))
            
            # Try to fetch the website
            response = self.session.get(website_url, timeout=5, allow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Method 1: Look for mailto: links
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
            if mailto_links:
                email = mailto_links[0]['href'].replace('mailto:', '').split('?')[0]
                if self._is_valid_email(email):
                    self.email_extraction_count += 1
                    return email.lower().strip()
            
            # Method 2: Search in common locations (contact, impressum, footer)
            priority_sections = soup.find_all(['footer', 'div', 'section'], 
                                             class_=re.compile(r'(contact|impressum|footer|kontakt)', re.I))
            for section in priority_sections:
                text = section.get_text()
                emails = self._extract_emails_from_text(text)
                if emails:
                    self.email_extraction_count += 1
                    return emails[0]
            
            # Method 3: Search entire page text as fallback
            page_text = soup.get_text()
            emails = self._extract_emails_from_text(page_text)
            if emails:
                self.email_extraction_count += 1
                return emails[0]
            
            return None
            
        except requests.RequestException:
            # Website not accessible, skip silently
            return None
        except Exception:
            # Any other error, skip silently
            return None
    
    def _extract_emails_from_text(self, text: str) -> List[str]:
        """Extract and prioritize email addresses from text"""
        if not text:
            return []
        
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = re.findall(email_pattern, text)
        
        if not found_emails:
            return []
        
        # Filter valid emails
        valid_emails = [e.lower().strip() for e in found_emails if self._is_valid_email(e)]
        
        if not valid_emails:
            return []
        
        # Prioritize business emails over personal/generic
        priority_prefixes = ['info', 'contact', 'kontakt', 'mail', 'hello', 'reservierung', 'reservation']
        avoid_prefixes = ['noreply', 'no-reply', 'privacy', 'support', 'abuse']
        
        # Sort by priority
        prioritized = []
        others = []
        
        for email in valid_emails:
            local_part = email.split('@')[0].lower()
            
            # Skip unwanted emails
            if any(avoid in local_part for avoid in avoid_prefixes):
                continue
            
            # Prioritize business emails
            if any(prefix in local_part for prefix in priority_prefixes):
                prioritized.append(email)
            else:
                others.append(email)
        
        return prioritized + others
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format and exclude common fake/placeholder emails"""
        if not email:
            return False
        
        # Exclude common placeholders
        excluded_domains = ['example.com', 'test.com', 'domain.com', 'email.com', 'yoursite.com']
        excluded_patterns = ['@image', '@photo', '.png', '.jpg', '.gif', '@fb.', '@twitter']
        
        email_lower = email.lower()
        
        # Check for excluded domains
        if any(domain in email_lower for domain in excluded_domains):
            return False
        
        # Check for excluded patterns (social media, images)
        if any(pattern in email_lower for pattern in excluded_patterns):
            return False
        
        # Basic format validation
        if len(email) < 6 or len(email) > 320:
            return False
        
        if '@' not in email or email.count('@') != 1:
            return False
        
        local, domain = email.split('@')
        if not local or not domain or '.' not in domain:
            return False
        
        return True

    def enrich_with_emails(self, results: List[Dict]) -> List[Dict]:
        """
        Enrich results with email addresses extracted from websites
        
        Args:
            results: List of place results with website URLs
            
        Returns:
            Same results with email field populated where possible
        """
        if not self.enable_email_extraction:
            return results
        
        print(f"\n    📧 Extracting emails from {len(results)} websites...")
        
        for i, result in enumerate(results):
            website = result.get('website', '')
            if website and website != 'N/A':
                email = self.extract_email_from_website(website)
                if email:
                    result['email'] = email
                    if (i + 1) % 10 == 0:
                        print(f"    📧 Progress: {i + 1}/{len(results)} - {self.email_extraction_count} emails found")
        
        print(f"    ✅ Email extraction complete: {self.email_extraction_count} emails found")
        return results
