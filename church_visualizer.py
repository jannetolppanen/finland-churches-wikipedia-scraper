# Piirtää kirkot kartalle ja tekee statseja
import json
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import defaultdict

class ChurchVisualizer:
    def __init__(self, input_file='output/churches_with_coordinates.json'):
        print(input_file)
        self.input_file = input_file
        self.churches = self.load_churches()

    def load_churches(self):
        """Load the churches from the JSON file"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File {self.input_file} not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {self.input_file}")
            return []

    def filter_valid_churches(self):
        """Filter out churches without valid coordinates"""
        valid_churches = []

        for church in self.churches:
            coords = church.get('coordinates', {})
            if coords and 'lat' in coords and 'lon' in coords:
                # Make sure coordinates are numbers
                try:
                    lat = float(coords['lat'])
                    lon = float(coords['lon'])

                    # Check if coordinates are in a reasonable range for Finland
                    if 59 <= lat <= 71 and 19 <= lon <= 32:
                        church['coordinates']['lat'] = lat
                        church['coordinates']['lon'] = lon
                        valid_churches.append(church)
                except (ValueError, TypeError):
                    pass

        return valid_churches

    def create_map(self, output_file='output/finnish_churches_map.html'):
        """Create an interactive map of the churches"""
        # Filter churches with valid coordinates
        valid_churches = self.filter_valid_churches()

        if not valid_churches:
            print("No churches with valid coordinates found.")
            return

        # Create a map centered on Finland
        m = folium.Map(location=[64.5, 26.0], zoom_start=6)

        # Add marker clusters
        marker_cluster = MarkerCluster().add_to(m)

        # Add markers for each church
        for church in valid_churches:
            lat = church['coordinates']['lat']
            lon = church['coordinates']['lon']

            # Create popup content
            popup_html = f"""
            <b>{church['name']}</b><br>
            """

            if church.get('address'):
                popup_html += f"Address: {church['address']}<br>"

            popup_html += f"""
            Coordinates: {lat:.6f}, {lon:.6f}<br>
            <a href="{church['wikipedia_link']}" target="_blank">Wikipedia Page</a>
            """

            # Add marker to cluster
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=church['name'],
                icon=folium.Icon(icon="church", prefix="fa")
            ).add_to(marker_cluster)

        # Save the map
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        m.save(output_file)

        print(f"Map with {len(valid_churches)} churches created: {output_file}")
        return valid_churches

    def create_statistics(self, output_dir='output/statistics'):
        """Create statistics and charts about the churches"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Count details
        counts = defaultdict(int)
        for church in self.churches:
            has_lat_lon = 'coordinates' in church and 'lat' in church['coordinates'] and 'lon' in church['coordinates']
            has_detailed_address = 'detailed_address' in church and church['detailed_address']
            has_address = 'address' in church and church['address'].strip()
            if has_lat_lon:
                counts['churches_with_lat_lon'] += 1
            elif has_detailed_address:
                counts['detailed_address'] += 1
            elif has_address:
                counts['non_detailed_address'] += 1
            else:
                counts['no_details'] += 1

        # Create pie chart
        plt.figure(figsize=(10, 6))
        labels = ['Valid Coordinates', 'Detailed Address', 'Non-Detailed Address', 'No Details']
        sizes = [counts['churches_with_lat_lon'], counts['detailed_address'], counts['non_detailed_address'], counts['no_details']]
        colors = ['gold', 'lightgreen', 'lightcoral', 'lightskyblue']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, shadow=True)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Churches Statistics', fontsize=16)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/churches_statistics_pie.png")
        plt.close()

        # Create bar chart
        plt.figure(figsize=(12, 6))
        plt.bar(labels, sizes, color=colors)
        plt.title('Number of Churches by Address Status', fontsize=16)
        plt.xlabel('Address Status', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.xticks(rotation=0, fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Add count labels on top of bars
        for i, count in enumerate(sizes):
            plt.text(i, count + 0.5, str(count), ha='center', fontsize=12)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/churches_statistics_bar.png")
        plt.close()

        # Create a summary text file
        with open(f"{output_dir}/summary.txt", 'w', encoding='utf-8') as f:
            f.write("Finnish Churches Statistics\n")
            f.write("==========================\n\n")
            f.write(f"Total churches with valid coordinates: {counts['churches_with_lat_lon']}\n")
            f.write(f"Churches with detailed address: {counts['detailed_address']}\n")
            f.write(f"Churches with non-detailed address: {counts['non_detailed_address']}\n")
            f.write(f"Churches with no details: {counts['no_details']}\n\n")

        print(f"Statistics created in directory: {output_dir}")

def main():
    print("Starting Finnish Churches Visualization")
    print("=======================================")

    input_file = 'output\churches_with_coordinates_updated_from_addresses.json'

    visualizer = ChurchVisualizer(input_file)
    valid_churches = visualizer.create_map()

    if valid_churches:
        visualizer.create_statistics()

    print("\nVisualization completed!")

if __name__ == "__main__":
    main()