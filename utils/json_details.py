import json
from collections import defaultdict

def merge_json_keys(json_obj):
    def recursive_keys(obj, keys_dict):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key not in keys_dict:
                    keys_dict[key] = {}
                recursive_keys(value, keys_dict[key])
        elif isinstance(obj, list):
            for item in obj:
                recursive_keys(item, keys_dict)

    keys_dict = {}
    recursive_keys(json_obj, keys_dict)
    return keys_dict

def count_details(json_obj):
    counts = defaultdict(int)

    for obj in json_obj:
        has_lat_lon = 'coordinates' in obj and 'lat' in obj['coordinates'] and 'lon' in obj['coordinates']
        has_detailed_address = 'detailed_address' in obj and obj['detailed_address']
        has_address = 'address' in obj and obj['address'].strip()

        if has_lat_lon:
            counts['churches_with_lat_lon'] += 1
        elif has_detailed_address:
            counts['detailed_address'] += 1
        elif has_address:
            counts['non_detailed_address'] += 1
        else:
            counts['no_details'] += 1

    return counts

# Example usage:
json_file_path = 'output\churches_with_coordinates_updated_from_addresses.json'
with open(json_file_path, 'r', encoding='utf-8') as file:
    json_obj = json.load(file)

if __name__ == '__main__':
    # result = merge_json_keys(json_obj)
    # print(json.dumps(result, indent=4))

    counts = count_details(json_obj)
    print("Counts of details:", json.dumps(counts, indent=4))

