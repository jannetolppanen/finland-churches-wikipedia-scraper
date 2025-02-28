import requests
import json
import os

def get_coordinates_from_address(address):
    """
    Main function that retrieves latitude and longitude from an address using OSM Nominatim API.
    
    Parameters:
    address (str): The street address to geocode
    
    Returns:
    tuple: (latitude, longitude) if found, otherwise None
    """
    # Format the address for a URL
    headers = {
        'User-Agent': 'CoordinatesApp/1.0',  # Replace with your app name - required by Nominatim usage policy
        'Accept-Language': 'en'  # Optional - language preference for results
    }
    
    # Create the API URL
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    
    try:
        # Helper function that makes the actual HTTP request
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return (lat, lon)
        else:
            print("No results found for this address")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates: {e}")
        return None

def process_json_file(file_path, output_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for church in data:
        if 'address' not in church:
            continue
        
        address = church['address']
        coordinates = get_coordinates_from_address(address)
        if coordinates:
            lat, lon = coordinates
            church['coordinates']['lat'] = lat
            church['coordinates']['lon'] = lon
        else:
            church['coordinates']['lat'] = None
            church['coordinates']['lon'] = None

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=4)

# Example usage
if __name__ == "__main__":
  input_file = "churches_without_location.json"
  output_file = "output/test/churches_with_coordinates_from_manual_address.json"

  process_json_file(input_file, output_file)








