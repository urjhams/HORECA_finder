"""
Search Configuration for HORECA Distributor Finder
==================================================
This file contains the location data and search queries used by the main script.
"""

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
