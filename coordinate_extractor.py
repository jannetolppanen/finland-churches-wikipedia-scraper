# Kaivaa yksittäisestä jsonista wikipedialinkit ja kaivaa osoitteet ja koordinaatit
import json
import re
import time
import requests
from bs4 import BeautifulSoup
import random

class CoordinateExtractor:
    def __init__(self, input_file='output/all_churches_with_coordinates.json', output_file='output/churches_with_coordinates.json'):
        self.input_file = input_file
        self.output_file = output_file
        # Add counters for method statistics
        self.method_stats = {
            "method_1": 0,
            "method_2": 0,
            "method_3": 0,
            "method_4": 0,  # Method for wgCoordinates in RLCONF
            "method_5": 0,  # Method for geo metadata tags
            "no_coords": 0,
            "address_found": 0,
            "detailed_address": 0
        }
        
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
                "original": f"{lat_dms}, {lon_dms}",
                "method": "method_1"
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
                "original": coord_text,
                "method": "method_1"
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
                "original": f"{lat_dms}, {lon_dms}",
                "method": "method_2"
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
                "original": f"{lat_dms}, {lon_dms}",
                "method": "method_3"
            }
        
        return None
    
    def extract_coordinates_method_4(self, soup):
        """
        Method 4: Extract coordinates from the script section containing wgCoordinates
        Example: "wgCoordinates":{"lat":61.29861666666667,"lon":25.681866666666668}
        """
        # Look for script tags
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if script.string:
                # Search for wgCoordinates in the script content
                coords_match = re.search(r'"wgCoordinates":\s*{\s*"lat":\s*([\d\.-]+),\s*"lon":\s*([\d\.-]+)\s*}', script.string)
                if coords_match:
                    lat = float(coords_match.group(1))
                    lon = float(coords_match.group(2))
                    
                    return {
                        "lat": lat,
                        "lon": lon,
                        "format": "decimal",
                        "original": f"wgCoordinates: {lat}, {lon}",
                        "method": "method_4"
                    }
        
        return None
        
    def extract_coordinates_method_5(self, soup):
        """
        Method 5: Extract coordinates from metadata (Coordinates tag in head section)
        Some pages have coordinates in meta tags rather than in the visible content
        """
        # First check if there's a meta tag with geo position
        meta_geo = soup.find('meta', attrs={'name': 'geo.position'})
        if meta_geo and meta_geo.get('content'):
            content = meta_geo.get('content')
            coords = content.split(';')
            if len(coords) == 2:
                try:
                    lat = float(coords[0].strip())
                    lon = float(coords[1].strip())
                    return {
                        "lat": lat,
                        "lon": lon,
                        "format": "decimal",
                        "original": f"meta geo.position: {content}",
                        "method": "method_5"
                    }
                except ValueError:
                    pass
        
        # Look for hidden spans with geo microformat
        geo_span = soup.find('span', class_='geo')
        if geo_span:
            coords_text = geo_span.get_text().strip()
            coords_match = re.match(r'([\d\.-]+);\s*([\d\.-]+)', coords_text)
            if coords_match:
                try:
                    lat = float(coords_match.group(1))
                    lon = float(coords_match.group(2))
                    return {
                        "lat": lat,
                        "lon": lon,
                        "format": "decimal",
                        "original": f"geo microformat: {coords_text}",
                        "method": "method_5"
                    }
                except ValueError:
                    pass
        
        return None
    
    def enhanced_extract_address(self, soup):
        """
        Enhanced address extraction that can handle various Wikipedia infobox formats
        and prioritizes detailed addresses (street name & number, city)
        """
        # Find the infobox table
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return None
        
        # Look for "Sijainti" (Location) row
        address = None
        
        # Method 1: Standard format - look for th/td with "Sijainti" text
        for row in infobox.find_all('tr'):
            header = row.find(['th', 'td'], string=lambda text: text and 'Sijainti' in text)
            if header:
                td = row.find('td', recursive=False) if header.name == 'th' else header.find_next('td')
                if td:
                    address = td.get_text().strip()
                    # Clean up the address
                    address = re.sub(r'\s+', ' ', address)
                    print(f"  - Found address using method 1: {address}")
                    break
        
        # Method 2: Alternative format - look for "font-weight:bold" style in td
        if not address:
            for row in infobox.find_all('tr'):
                td = row.find('td', style=lambda style: style and 'font-weight:bold' in style)
                if td and 'Sijainti' in td.get_text():
                    value_td = td.find_next('td')
                    if value_td:
                        address = value_td.get_text().strip()
                        address = re.sub(r'\s+', ' ', address)
                        print(f"  - Found address using method 2: {address}")
                        break
        
        # If we found an address, check if it's a detailed one
        if address:
            # Check if it has both a street number and a city (comma separated)
            has_street_number = bool(re.search(r'\d+', address))
            has_comma = ',' in address
            
            if has_street_number and has_comma:
                return address
            else:
                print(f"  - Found address but it may not be detailed enough: {address}")
                # Still return it, but log that it might not be ideal
                return address
        
        return None
        
    def extract_address(self, soup):
        """
        Extract address from the infobox (legacy method kept for compatibility)
        Now calls the enhanced version
        """
        return self.enhanced_extract_address(soup)
    
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
        
        # Count how many churches already have coordinates and addresses
        already_with_coords = sum(1 for church in churches if church.get('coordinates'))
        already_with_address = sum(1 for church in churches if church.get('address'))
        
        print(f"Already have coordinates for {already_with_coords}/{len(churches)} churches.")
        print(f"Already have addresses for {already_with_address}/{len(churches)} churches.")
        
        processed_count = 0
        skipped_count = 0
        
        for i, church in enumerate(churches):
            # Skip churches that already have coordinates
            # (If we have coordinates, we don't need to extract the address)
            if church.get('coordinates'):
                skipped_count += 1
                continue
                
            print(f"\n[{i+1}/{len(churches)}] Processing: {church['name']}")
            processed_count += 1
            
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
                self.method_stats["method_1"] += 1
            else:
                # Method 2
                coords = self.extract_coordinates_method_2(soup)
                if coords:
                    print(f"  - Found coordinates using method 2: {coords['lat']}, {coords['lon']}")
                    church['coordinates'] = coords
                    self.method_stats["method_2"] += 1
                else:
                    # Method 3
                    coords = self.extract_coordinates_method_3(soup)
                    if coords:
                        print(f"  - Found coordinates using method 3: {coords['lat']}, {coords['lon']}")
                        church['coordinates'] = coords
                        self.method_stats["method_3"] += 1
                    else:
                        # Method 4
                        coords = self.extract_coordinates_method_4(soup)
                        if coords:
                            print(f"  - Found coordinates using method 4: {coords['lat']}, {coords['lon']}")
                            church['coordinates'] = coords
                            self.method_stats["method_4"] += 1
                        else:
                            # Method 5
                            coords = self.extract_coordinates_method_5(soup)
                            if coords:
                                print(f"  - Found coordinates using method 5: {coords['lat']}, {coords['lon']}")
                                church['coordinates'] = coords
                                self.method_stats["method_5"] += 1
                            else:
                                print(f"  - No coordinates found for {church['name']}")
                                self.method_stats["no_coords"] += 1
                                
                                # If we couldn't find coordinates, try to get the address as a fallback
                                if not church.get('address'):
                                    # Extract address using the enhanced method
                                    address = self.enhanced_extract_address(soup)
                                    if address:
                                        self.method_stats["address_found"] += 1
                                        church['address'] = address
                                        
                                        # Check if the address is detailed (has street number and comma)
                                        if ',' in address and re.search(r'\d+', address):
                                            self.method_stats["detailed_address"] += 1
                                            church['detailed_address'] = True
                                            print(f"  - Found detailed address as fallback: {address}")
                                        else:
                                            church['detailed_address'] = False
                                            print(f"  - Found address as fallback (not detailed): {address}")
                                    else:
                                        print(f"  - No address found as fallback for {church['name']}")
            
            # Save after each successful update to avoid losing progress
            if (i + 1) % 10 == 0:
                print(f"  - Saving progress after {i + 1} churches...")
                self.save_churches(churches)
        
        # Final save of all churches
        self.save_churches(churches)
        
        # Print summary
        with_coords = sum(1 for church in churches if church.get('coordinates'))
        with_address = sum(1 for church in churches if church.get('address'))
        with_detailed_address = sum(1 for church in churches if church.get('detailed_address', False))
        
        print("\nSummary:")
        print(f"- Total churches: {len(churches)}")
        print(f"- Processed churches: {processed_count}")
        print(f"- Skipped churches (already had coordinates): {skipped_count}")
        print(f"- Churches with coordinates: {with_coords} ({with_coords/len(churches)*100:.1f}%)")
        print(f"- Churches with any address: {with_address} ({with_address/len(churches)*100:.1f}%)")
        print(f"- Churches with detailed address: {with_detailed_address} ({with_detailed_address/len(churches)*100:.1f}%)")
        
        # Print method statistics (only for processed churches)
        if processed_count > 0:
            print("\nCoordinate Extraction Method Statistics (for processed churches):")
            print(f"- Method 1 (span id='coordinatespan'): {self.method_stats['method_1']} successes")
            print(f"- Method 2 (mw-indicator-AA-coordinates): {self.method_stats['method_2']} successes")
            print(f"- Method 3 (infobox table): {self.method_stats['method_3']} successes")
            print(f"- Method 4 (wgCoordinates in script): {self.method_stats['method_4']} successes")
            print(f"- Method 5 (geo metadata): {self.method_stats['method_5']} successes")
            print(f"- No coordinates found: {self.method_stats['no_coords']} churches")
            
            print("\nAddress Extraction Statistics (for processed churches):")
            print(f"- Churches with any address found: {self.method_stats['address_found']} churches")
            print(f"- Churches with detailed address found: {self.method_stats['detailed_address']} churches")
        
        print(f"\n- Results saved to {self.output_file}")

def test_single_page(html_file, verbose=True):
    """
    Test the coordinate and address extraction methods on a single HTML file.
    This is useful for debugging and testing new extraction methods.
    
    Args:
        html_file (str): Path to an HTML file to test
        verbose (bool): Whether to print detailed information
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    extractor = CoordinateExtractor()
    
    print(f"\n===== Testing Coordinate Extraction on {html_file} =====")
    
    # Try all coordinate extraction methods
    methods = [
        ("Method 1 (span id='coordinatespan')", extractor.extract_coordinates_method_1),
        ("Method 2 (mw-indicator-AA-coordinates)", extractor.extract_coordinates_method_2),
        ("Method 3 (infobox table)", extractor.extract_coordinates_method_3),
        ("Method 4 (wgCoordinates in script)", extractor.extract_coordinates_method_4),
        ("Method 5 (geo metadata)", extractor.extract_coordinates_method_5)
    ]
    
    found_coords = False
    for method_name, method_func in methods:
        coords = method_func(soup)
        if coords:
            found_coords = True
            print(f"- {method_name}: SUCCESS")
            print(f"  Lat: {coords['lat']}, Lon: {coords['lon']}")
            print(f"  Format: {coords['format']}")
            print(f"  Original: {coords['original']}")
        else:
            print(f"- {method_name}: FAILED")
    
    if not found_coords:
        print("No coordinates found with any method!")
    
    # Test address extraction
    print("\n===== Testing Address Extraction =====")
    address = extractor.enhanced_extract_address(soup)
    
    if address:
        print(f"Found address: {address}")
        
        # Check if it's a detailed address
        if ',' in address and re.search(r'\d+', address):
            print("This is a detailed address (contains street number and comma)")
        else:
            print("This is NOT a detailed address")
    else:
        print("No address found")
    
    return {
        "coordinates": found_coords,
        "address": address is not None
    }

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        if len(sys.argv) > 2:
            # Test a specific HTML file
            test_single_page(sys.argv[2])
        else:
            print("Please specify an HTML file to test")
            print("Usage: python coordinate_extractor.py --test <html_file>")
    else:
        # Normal processing mode
        extractor = CoordinateExtractor()
        extractor.process_churches()

if __name__ == "__main__":
    main()