import csv
import sys
import os

# Paths relative to script location
INPUT_FILE = os.path.join("Data", "products.csv")
OUTPUT_FILE = os.path.join("Data", "products_clean.csv")

def clean_csv():
    print(f"Reading from: {INPUT_FILE}")
    
    with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f_in:
        reader = csv.reader(f_in)
        header = next(reader)
        
        # Identify the non-empty columns in header
        valid_headers = [h for h in header if h.strip()]
        num_columns = len(valid_headers)
        
        print(f"Detected {num_columns} valid columns: {valid_headers}")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(valid_headers)
            
            count = 0
            empty_rows = 0
            
            for row in reader:
                cleaned_row = row[:num_columns]
                
                # Check if row is essentially empty
                if not any(cell.strip() for cell in cleaned_row):
                    empty_rows += 1
                    continue
                
                # Check required fields (e.g. part_number at index 0)
                if not cleaned_row[0].strip():
                     # print(f"Skipping row {count+2} (missing part_number)")
                     continue

                writer.writerow(cleaned_row)
                count += 1
                
            print(f"Cleaned {count} rows.")
            print(f"Removed {empty_rows} empty rows.")
            print(f"Output saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_csv()
