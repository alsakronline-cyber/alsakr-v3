import os
import requests
import json
import random

# Configuration
API_URL = "http://localhost:8090"  # PocketBase URL
ES_URL = "http://localhost:9200"   # Elasticsearch URL

# Dummy Vendors
VENDORS = [
    {
        "company_name": "TechSupply Co.",
        "contact_name": "John Smith",
        "email": "sales@techsupply.com",
        "phone": "+1-555-0101",
        "address": "123 Tech Blvd, Silicon Valley, CA",
        "rating": 4.8,
        "specialties": ["Sensors", "Automation"]
    },
    {
        "company_name": "Industrial Parts Ltd",
        "contact_name": "Sarah Connor",
        "email": "orders@ind-parts.com",
        "phone": "+44-20-7946-0958",
        "address": "45 Factory Lane, Manchester, UK",
        "rating": 4.5,
        "specialties": ["Motors", "Drives"]
    },
    {
        "company_name": "Global Sourcing Hub",
        "contact_name": "Wei Zhang",
        "email": "wei@global-source.cn",
        "phone": "+86-21-1234-5678",
        "address": "88 Innovation Way, Shanghai, CN",
        "rating": 4.2,
        "specialties": ["General Components", "Cables"]
    },
    {
        "company_name": "FastTrack Logistics",
        "contact_name": "Hans Muller",
        "email": "hans@fasttrack.de",
        "phone": "+49-30-123456",
        "address": "Indstriestr. 9, Berlin, DE",
        "rating": 4.9,
        "specialties": ["Urgent Delivery", "Safety Systems"]
    },
     {
        "company_name": "Alpha Components",
        "contact_name": "Alice Johnson",
        "email": "alice@alpha.com",
        "phone": "+1-555-0102",
        "address": "789 Alpha Ave, New York, NY",
        "rating": 4.6,
        "specialties": ["Connectors", "Switches"]
    }
]

# Dummy Products (SICK style)
PRODUCTS = [
    {
        "part_number": "1044356",
        "name": "WSE4S-3P2230",
        "category": "Photoelectric sensors",
        "description": "Miniature photoelectric sensors, W4S-3, Sensing range max.: 0 m ... 5 m",
        "stock": 150,
        "price": 85.00
    },
    {
        "part_number": "1042049",
        "name": "WTB4-3P1361",
        "category": "Photoelectric sensors",
        "description": "Miniature photoelectric sensors, W4-3, Sensing range max.: 4 mm ... 150 mm",
        "stock": 42,
        "price": 62.50
    },
    {
        "part_number": "6047683",
        "name": "DFS60B-S4EA01024",
        "category": "Encoders",
        "description": "Incremental encoders, DFS60, Pulses per revolution: 1,024",
        "stock": 8,
        "price": 220.00
    },
    {
        "part_number": "1215492",
        "name": "LFP1000-A4NMB",
        "category": "Level sensors",
        "description": "TDR level sensor, LFP Cubic, Probe length: 1,000 mm",
        "stock": 3,
        "price": 450.00
    },
    {
         "part_number": "2055478",
         "name": "BEF-WN-W23",
         "category": "Mounting systems",
         "description": "Mounting brackets and plates, Mounting bracket",
         "stock": 500,
         "price": 12.00
    },
     {
        "part_number": "1023456",
        "name": "WL12-3P2431",
        "category": "Photoelectric sensors",
        "description": "Small photoelectric sensors, W12-3, Sensing range max.: 0 m ... 7 m",
        "stock": 88,
        "price": 95.00
    },
    {
        "part_number": "6037854",
        "name": "DBS36E-S3AK01024",
        "category": "Encoders",
        "description": "Incremental encoders, DBS36/50, Pulses per revolution: 1,024",
        "stock": 25,
        "price": 110.00
    },
     {
        "part_number": "7900258",
        "name": "YF2A14-050VB3XLEAX",
        "category": "Plug connectors and cables",
        "description": "Sensor/actuator cable, 4-wire, PVC, 5 m, M12",
        "stock": 1000,
        "price": 18.50
    }
]

def seed_vendors():
    print("Seeding Vendors...")
    # This logic assumes we have a working PocketBase instance or similar.
    # For now, we'll just print what we WOULLD do, because I don't want to break the user's DB if PB isn't running.
    # But wait, the user asked to "create dummy data".
    # I should try to hit the API if possible, or just create a JSON file that the backend can load.
    
    # Better approach: Create a JSON file `dummy_data.json` in `backend/app/data` 
    # and have the MultiVendor agent read from it if DB fails or for "simulation".
    pass

def create_dummy_json():
    data = {
        "vendors": VENDORS,
        "products": PRODUCTS
    }
    
    os.makedirs("v2_project/backend/app/data", exist_ok=True)
    with open("v2_project/backend/app/data/dummy_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Created v2_project/backend/app/data/dummy_data.json")

if __name__ == "__main__":
    create_dummy_json()
