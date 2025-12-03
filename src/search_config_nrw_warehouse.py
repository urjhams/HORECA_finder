NRW_LOCATIONS = {
    "Duisburg": {"lat": 51.43, "lng": 6.77, "radius": 40},  # Europe's largest inland port
    "Cologne": {"lat": 50.94, "lng": 6.96, "radius": 40},   # Major distribution hub
    "Düsseldorf": {"lat": 51.22, "lng": 6.78, "radius": 40},# State capital, logistics cluster
    "Dortmund": {"lat": 51.51, "lng": 7.47, "radius": 40},  # Ruhr region center
    "Essen": {"lat": 51.46, "lng": 7.01, "radius": 40},     # Ruhr industrial zone
    "Bonn": {"lat": 50.74, "lng": 7.10, "radius": 35},      # South NRW logistics
    "Wuppertal": {"lat": 51.26, "lng": 7.15, "radius": 35}, # Bergisches Land industrial
    "Münster": {"lat": 51.96, "lng": 7.63, "radius": 35},   # Northern NRW distribution
    "Bielefeld": {"lat": 52.02, "lng": 8.53, "radius": 35}, # Eastern NRW, near A2 highway
    "Aachen": {"lat": 50.78, "lng": 6.08, "radius": 35},    # Western border, near Belgium/Netherlands
}

NRW_QUERIES_GERMAN = [
    "Tiefkühlkost Lager Nordrhein-Westfalen",           # Frozen food warehouse NRW
    "Kühlhaus Palettenplätze NRW",                      # Cold storage pallet spaces NRW
    "Kaltlager Logistikzentrum NRW",                    # Cold storage logistics center NRW
    "Tiefkühlkost Logistik NRW",                        # Frozen food logistics NRW
    "Kühlhaus 150 Paletten NRW",                        # Cold storage 150 pallets NRW
    "Frostlager Duisburg",                              # Freezer warehouse Duisburg
    "Kühlhaus Köln",                                    # Cold storage Cologne
    "Logistikzentrum Düsseldorf Tiefkühl",              # Logistics center Düsseldorf frozen
]

NRW_QUERIES_ENGLISH = [
    "frozen food warehouse NRW",                        # English version
    "cold storage logistics NRW",                       # English cold storage
    "pallet spaces warehouse NRW",                      # English pallet spaces
    "temperature controlled warehouse NRW",             # Temperature controlled warehouse
]

# pronpt = f"""
# Company: {record['company_name']}
# Address: {record['full_address']}
# Phone: {record.get('phone', 'N/A')}
# Website: {record.get('website', 'N/A')}
# Description: {record.get('raw_description', '')}

# Classify this business:

# 1. is_cold_storage_warehouse (true/false): Does this appear to be a cold/frozen storage warehouse?
# 2. likely_pallet_capacity (none/low/medium/high): Estimate pallet capacity (high = 150+ pallets likely)
# 3. is_logistics_center (true/false): Is this a logistics/distribution center?
# 4. priority_score (1-10): Overall fit for frozen food warehouse with 150+ pallets

# Return JSON only.
# """