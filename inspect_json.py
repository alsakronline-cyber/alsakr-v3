import json
import os

INPUT_FILE = os.path.join("Data", "products.json")

def inspect_json():
    print(f"Reading from: {INPUT_FILE}")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            print(f"Found list with {len(data)} items")
            if data:
                print("First item sample:")
                print(json.dumps(data[0], indent=2))
        else:
            print("Root element is not a list")
            print(str(type(data)))
            
    except Exception as e:
        print(f"Error reading JSON: {e}")

if __name__ == "__main__":
    inspect_json()
