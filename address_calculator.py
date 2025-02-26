## Antaa tiedot monellako kirkolla on osoite ja/tai koordinaatit
import json
import re

# Load the JSON file
with open("output/churches_with_coordinates.json", 'r', encoding='utf-8') as f:
    churches = json.load(f)

# Initialize counters
total_churches = len(churches)
with_coordinates = 0
with_detailed_address = 0
with_undetailed_address = 0
without_any_location = 0
with_coords_and_address = 0
with_coords_only = 0
with_address_only = 0

# Analyze each church
for church in churches:
    # Check for coordinates
    has_coordinates = False
    if "coordinates" in church and church["coordinates"] is not None:
        if "lat" in church["coordinates"] and "lon" in church["coordinates"]:
            has_coordinates = True
    
    # Check for address and if it's detailed
    has_detailed_address = False
    has_address = False
    
    if "address" in church and church["address"] is not None:
        address = church["address"]
        has_address = True
        
        # Check if it's a detailed address (has street number and comma)
        if ',' in address and re.search(r'\d+', address):
            has_detailed_address = True
    
    # Update statistics
    if has_coordinates and has_address:
        with_coords_and_address += 1
        with_coordinates += 1
        if has_detailed_address:
            with_detailed_address += 1
        else:
            with_undetailed_address += 1
    elif has_coordinates:
        with_coords_only += 1
        with_coordinates += 1
    elif has_address:
        with_address_only += 1
        if has_detailed_address:
            with_detailed_address += 1
        else:
            with_undetailed_address += 1
    else:
        without_any_location += 1

# Calculate percentages
percent_with_coords = (with_coordinates / total_churches) * 100
percent_with_detailed = (with_detailed_address / total_churches) * 100
percent_with_undetailed = (with_undetailed_address / total_churches) * 100
percent_without_location = (without_any_location / total_churches) * 100

# Print statistics
print("=== CHURCH LOCATION STATISTICS ===")
print(f"Total churches: {total_churches}")
print("\n=== COORDINATES ===")
print(f"Churches with coordinates: {with_coordinates} ({percent_with_coords:.1f}%)")

print("\n=== ADDRESSES ===")
print(f"Churches with detailed address: {with_detailed_address} ({percent_with_detailed:.1f}%)")
print(f"Churches with undetailed address: {with_undetailed_address} ({percent_with_undetailed:.1f}%)")
print(f"Total churches with any address: {with_detailed_address + with_undetailed_address}")

print("\n=== COMBINED INFORMATION ===")
print(f"Churches with both coordinates and address: {with_coords_and_address}")
print(f"Churches with coordinates only: {with_coords_only}")
print(f"Churches with address only: {with_address_only}")
print(f"Churches without any location: {without_any_location} ({percent_without_location:.1f}%)")

# Verify that numbers add up
total_check = with_coords_and_address + with_coords_only + with_address_only + without_any_location
print(f"\nVerification - Sum of categories: {total_check} (should equal {total_churches})")

# Save churches without location to a file
churches_without_location = [
    church for church in churches 
    if (("coordinates" not in church or church["coordinates"] is None or 
         "lat" not in church["coordinates"] or "lon" not in church["coordinates"]) and
        ("address" not in church or church["address"] is None))
]

with open('churches_without_location.json', 'w', encoding='utf-8') as f:
    json.dump(churches_without_location, indent=4, ensure_ascii=False, fp=f)

print(f"\nSaved {len(churches_without_location)} churches without location to 'churches_without_location.json'")