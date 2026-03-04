"""
Search Configuration for HORECA Distributor Finder
==================================================
This file contains the location data and search queries used by the main script.
"""

# ============================================================================
# LOCATION DATA: Germany comprehensive coverage with tiered radius
# ============================================================================

SEARCH_LOCATIONS = {
    "Germany": {
        "tier_1_mega": [  # 5-10 km radius (High density - multiple calls per city needed for full coverage)
            {"name": "Berlin-Center", "lat": 52.52, "lng": 13.40, "radius": 10},
            {"name": "Hamburg-Center", "lat": 53.55, "lng": 10.00, "radius": 10},
            {"name": "Munich-Center", "lat": 48.14, "lng": 11.58, "radius": 10},
            {"name": "Cologne-Center", "lat": 50.94, "lng": 6.96, "radius": 10},
            {"name": "Frankfurt-Center", "lat": 50.11, "lng": 8.68, "radius": 10}
        ],
        "tier_2_large": [  # 15-20 km radius
            {"name": "Stuttgart", "lat": 48.78, "lng": 9.18, "radius": 15},
            {"name": "Düsseldorf", "lat": 51.22, "lng": 6.78, "radius": 15},
            {"name": "Leipzig", "lat": 51.34, "lng": 12.37, "radius": 20},
            {"name": "Dortmund (Ruhr Area)", "lat": 51.51, "lng": 7.46, "radius": 15},
            {"name": "Essen (Ruhr Area)", "lat": 51.45, "lng": 7.01, "radius": 15},
            {"name": "Bremen", "lat": 53.07, "lng": 8.81, "radius": 20},
            {"name": "Dresden", "lat": 51.05, "lng": 13.73, "radius": 20}
        ],
        "tier_3_regional": [  # 25 km radius
            {"name": "Hanover", "lat": 52.37, "lng": 9.73, "radius": 25},
            {"name": "Nuremberg", "lat": 49.45, "lng": 11.08, "radius": 25},
            {"name": "Duisburg", "lat": 51.43, "lng": 6.76, "radius": 20},
            {"name": "Wandsbek", "lat": 53.57, "lng": 10.07, "radius": 20},
            {"name": "Bochum", "lat": 51.48, "lng": 7.21, "radius": 20},
            {"name": "Wuppertal", "lat": 51.25, "lng": 7.15, "radius": 20},
            {"name": "Bielefeld", "lat": 52.03, "lng": 8.53, "radius": 25},
            {"name": "Bonn", "lat": 50.73, "lng": 7.10, "radius": 25},
            {"name": "Münster", "lat": 51.96, "lng": 7.62, "radius": 25},
            {"name": "Karlsruhe", "lat": 49.00, "lng": 8.40, "radius": 25},
            {"name": "Mannheim", "lat": 49.48, "lng": 8.46, "radius": 25},
            {"name": "Augsburg", "lat": 48.37, "lng": 10.89, "radius": 25}
        ],
        "tier_4_gaps": [  # 35-50 km radius (Rural/Coverage gaps)
            {"name": "Freiburg (Southwest)", "lat": 47.99, "lng": 7.84, "radius": 35},
            {"name": "Rostock (North)", "lat": 54.09, "lng": 12.10, "radius": 40},
            {"name": "Kassel (Central)", "lat": 51.31, "lng": 9.47, "radius": 40},
            {"name": "Magdeburg (East)", "lat": 52.12, "lng": 11.62, "radius": 40},
            {"name": "Saarbrücken (West)", "lat": 49.23, "lng": 7.00, "radius": 40},
            {"name": "Regensburg (Southeast)", "lat": 49.01, "lng": 12.09, "radius": 40}
        ]
    }
}

# Search queries for Germany (restaurant-focused)
SEARCH_QUERIES = {
    "Germany": [
        "Restaurant",
        "Asiatisches Restaurant",
        "Vietnamesisches Restaurant",
        "Chinesisches Restaurant",
        "Türkisches Restaurant",
    ]
}
