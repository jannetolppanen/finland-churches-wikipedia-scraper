# coordinate_extractor.py
import json
import re
import time
import requests
from bs4 import BeautifulSoup
import random

class CoordinateExtractor:
    def __init__(self, input_file='output/catholic_churches.json', output_file='output/churches_with_coordinates.json'):
        self.input_file = input_file
        self.output_file = output_file
        
    def load_churches(self):
        """Load the churches from the JSON file"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File {self.input_file} not found.")
            return []
    
    def save_churches(self, churches):
        """Save the churches to the JSON file"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(churches, f, ensure_ascii=False, indent=4)
    
    def fetch_page(self, url):
        """Fetch the Wikipedia page with a delay to avoid hitting rate limits"""
        # Random delay between 1-3 seconds to be polite to Wikipedia
        time.sleep(random.uniform(1, 3))
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_coordinates_method_1(self, soup):
        """
        Method 1: Extract coordinates from the span with id="coordinatespan"
        Example: <span id="coordinatespan" class="plainlinksneverexpand">...
        """
        coord_span = soup.find('span', id='coordinatespan')
        if not coord_span:
            return None
        
        # Look for the actual coordinate text
        coord_text = coord_span.get_text().strip()
        
        # Extract latitude and longitude using regex
        lat_match = re.search(r'(\d+°\d+′\d+(?:\.\d+)?″[NS])', coord_text)
        lon_match = re.search(r'(\d+°\d+′\d+(?:\.\d+)?″[EW])', coord_text)
        
        if lat_match and lon_match:
            lat_dms = lat_match.group(1)
            lon_dms = lon_match.group(1)
            
            # Convert DMS to decimal degrees
            lat_decimal = self.dms_to_decimal(lat_dms)
            lon_decimal = self.dms_to_decimal(lon_dms)
            
            return {
                "lat": lat_decimal,
                "lon": lon_decimal,
                "format": "DMS",
                "original": f"{lat_dms}, {lon_dms}"
            }
        
        # Alternative format: decimal degrees
        decimal_match = re.search(r'(\d+\.\d+)°[NS].*?(\d+\.\d+)°[EW]', coord_text)
        if decimal_match:
            lat = float(decimal_match.group(1))
            lon = float(decimal_match.group(2))
            
            # Check if we need to negate based on direction
            if 'S' in coord_text:
                lat = -lat
            if 'W' in coord_text:
                lon = -lon
            
            return {
                "lat": lat,
                "lon": lon,
                "format": "decimal",
                "original": coord_text
            }
        
        return None
    
    def extract_coordinates_method_2(self, soup):
        """
        Method 2: Extract coordinates from the mw-indicator with id="mw-indicator-AA-coordinates"
        """
        indicator = soup.find('div', id='mw-indicator-AA-coordinates')
        if not indicator:
            return None
        
        coord_span = indicator.find('span', id='coordinatespan')
        if not coord_span:
            return None
        
        # Extract the text from the span
        coord_text = coord_span.get_text().strip()
        
        # Extract latitude and longitude using regex
        lat_match = re.search(r'(\d+°\d+′\d+(?:\.\d+)?″[NS])', coord_text)
        lon_match = re.search(r'(\d+°\d+′\d+(?:\.\d+)?″[EW])', coord_text)
        
        if lat_match and lon_match:
            lat_dms = lat_match.group(1)
            lon_dms = lon_match.group(1)
            
            # Convert DMS to decimal degrees
            lat_decimal = self.dms_to_decimal(lat_dms)
            lon_decimal = self.dms_to_decimal(lon_dms)
            
            return {
                "lat": lat_decimal,
                "lon": lon_decimal,
                "format": "DMS",
                "original": f"{lat_dms}, {lon_dms}"
            }
        
        return None
    
    def extract_coordinates_method_3(self, soup):
        """
        Method 3: Extract coordinates from the infobox table coordinates row
        """
        # Find the infobox table
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return None
        
        # Find the row with "Koordinaatit" label
        coord_row = None
        for row in infobox.find_all('tr'):
            th = row.find('th')
            if th and 'Koordinaatit' in th.get_text():
                coord_row = row
                break
        
        if not coord_row:
            return None
        
        # Get the coordinate text from the td
        td = coord_row.find('td')
        if not td:
            return None
        
        coord_span = td.find('span', id='coordinatespan')
        if not coord_span:
            return None
        
        # Extract the text
        coord_text = coord_span.get_text().strip()
        
        # Extract latitude and longitude using regex
        lat_match = re.search(r'(\d+°\d+′\d+(?:\.\d+)?″[NS])', coord_text)
        lon_match = re.search(r'(\d+°\d+′\d+(?:\.\d+)?″[EW])', coord_text)
        
        if lat_match and lon_match:
            lat_dms = lat_match.group(1)
            lon_dms = lon_match.group(1)
            
            # Convert DMS to decimal degrees
            lat_decimal = self.dms_to_decimal(lat_dms)
            lon_decimal = self.dms_to_decimal(lon_dms)
            
            return {
                "lat": lat_decimal,
                "lon": lon_decimal,
                "format": "DMS",
                "original": f"{lat_dms}, {lon_dms}"
            }
        
        return None
    
    def extract_address(self, soup):
        """Extract address from the infobox"""
        # Find the infobox table
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return None
        
        # Look for "Sijainti" (Location) row
        address = None
        for row in infobox.find_all('tr'):
            th = row.find('th')
            if th and 'Sijainti' in th.get_text():
                td = row.find('td')
                if td:
                    address = td.get_text().strip()
                    # Clean up the address
                    address = re.sub(r'\s+', ' ', address)
                    break
        
        return address
    
    def dms_to_decimal(self, dms_str):
        """Convert coordinates from DMS (Degrees, Minutes, Seconds) to decimal degrees"""
        # Parse DMS string like 60°09′33.2″N
        direction = dms_str[-1]
        dms_str = dms_str[:-1]  # Remove direction
        
        # Split the string into degrees, minutes, and seconds
        parts = re.findall(r'(\d+)°(\d+)′(\d+(?:\.\d+)?)″', dms_str)
        
        if parts:
            degrees, minutes, seconds = map(float, parts[0])
            decimal = degrees + minutes/60 + seconds/3600
            
            # Adjust sign based on direction
            if direction in ['S', 'W']:
                decimal = -decimal
            
            return decimal
        
        return None
    
    def process_churches(self):
        """Process all churches and extract coordinates"""
        churches = self.load_churches()
        if not churches:
            print("No churches loaded.")
            return
        
        print(f"Processing {len(churches)} churches...")
        
        for i, church in enumerate(churches):
            print(f"\n[{i+1}/{len(churches)}] Processing: {church['name']}")
            
            url = church['wikipedia_link']
            soup = self.fetch_page(url)
            
            if not soup:
                print(f"  - Failed to fetch page for {church['name']}")
                continue
            
            # Try all methods to extract coordinates
            coords = None
            
            # Method 1
            coords = self.extract_coordinates_method_1(soup)
            if coords:
                print(f"  - Found coordinates using method 1: {coords['lat']}, {coords['lon']}")
                church['coordinates'] = coords
            else:
                # Method 2
                coords = self.extract_coordinates_method_2(soup)
                if coords:
                    print(f"  - Found coordinates using method 2: {coords['lat']}, {coords['lon']}")
                    church['coordinates'] = coords
                else:
                    # Method 3
                    coords = self.extract_coordinates_method_3(soup)
                    if coords:
                        print(f"  - Found coordinates using method 3: {coords['lat']}, {coords['lon']}")
                        church['coordinates'] = coords
                    else:
                        print(f"  - No coordinates found for {church['name']}")
            
            # Extract address
            address = self.extract_address(soup)
            if address:
                print(f"  - Found address: {address}")
                church['address'] = address
            else:
                print(f"  - No address found for {church['name']}")
        
        # Save the updated churches
        self.save_churches(churches)
        
        # Print summary
        with_coords = sum(1 for church in churches if church.get('coordinates'))
        with_address = sum(1 for church in churches if church.get('address'))
        
        print("\nSummary:")
        print(f"- Total churches: {len(churches)}")
        print(f"- Churches with coordinates: {with_coords} ({with_coords/len(churches)*100:.1f}%)")
        print(f"- Churches with address: {with_address} ({with_address/len(churches)*100:.1f}%)")
        print(f"- Results saved to {self.output_file}")

def main():
    extractor = CoordinateExtractor()
    extractor.process_churches()

if __name__ == "__main__":
    main()
