import json
import os


file_path = r'output/churches_with_coordinates.json'
churches_with_detailed_address = []

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

stats = {
    
    "total_churches": len(data),
    "churches_with_coordinates": 0,
    "churches_with_detailed_address": 0,
    "churches_without_detailed_address": 0,
}

for church in data:
    # First get the 'coordinates' dictionary, then check if it has 'lat' and 'lon' keys
    coordinates = church.get('coordinates', {})
    if 'lat' in coordinates and 'lon' in coordinates:
        stats["churches_with_coordinates"] += 1
    
    elif church.get('detailed_address') == True:
        churches_with_detailed_address.append(church)
        stats["churches_with_detailed_address"] += 1
    else:
        stats["churches_without_detailed_address"] += 1


with open('output/churches_with_detailed_address.json', 'w', encoding='utf-8') as f:
    json.dump(churches_with_detailed_address, f, indent=4, ensure_ascii=False)

    print(stats)
    print('created output/churches_with_detailed_address.json')

