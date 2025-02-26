# Piirtää kirkot kartalle ja tekee statseja
import json
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import matplotlib.pyplot as plt
import os

class ChurchVisualizer:
    def __init__(self, input_file='output/churches_with_coordinates.json'):
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
            
            # Determine icon color based on church type
            if church.get('type') == 'Catholic':
                icon_color = 'red'
            elif church.get('type') == 'Orthodox':
                icon_color = 'blue'
            elif church.get('type') == 'Lutheran':
                icon_color = 'green'
            else:
                icon_color = 'gray'
            
            # Create popup content
            popup_html = f"""
            <b>{church['name']}</b><br>
            Type: {church.get('type', 'Unknown')}<br>
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
                icon=folium.Icon(color=icon_color, icon="church", prefix="fa")
            ).add_to(marker_cluster)
        
        # Save the map
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        m.save(output_file)
        
        print(f"Map with {len(valid_churches)} churches created: {output_file}")
        return valid_churches
    
    def create_statistics(self, output_dir='output/statistics'):
        """Create statistics and charts about the churches"""
        # Filter churches with valid coordinates
        valid_churches = self.filter_valid_churches()
        
        if not valid_churches:
            print("No churches with valid coordinates found.")
            return
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(valid_churches)
        
        # Extract lat/lon to separate columns
        df['lat'] = df['coordinates'].apply(lambda x: x.get('lat') if isinstance(x, dict) else None)
        df['lon'] = df['coordinates'].apply(lambda x: x.get('lon') if isinstance(x, dict) else None)
        
        # Count churches by type
        type_counts = df['type'].value_counts()
        
        # Create pie chart
        plt.figure(figsize=(10, 6))
        type_counts.plot.pie(autopct='%1.1f%%', startangle=90, fontsize=12)
        plt.title('Churches by Type', fontsize=16)
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/churches_by_type_pie.png")
        plt.close()
        
        # Create bar chart
        plt.figure(figsize=(12, 6))
        type_counts.plot.bar(color=['red', 'blue', 'green'])
        plt.title('Number of Churches by Type', fontsize=16)
        plt.xlabel('Church Type', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.xticks(rotation=0, fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add count labels on top of bars
        for i, count in enumerate(type_counts):
            plt.text(i, count + 0.5, str(count), ha='center', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/churches_by_type_bar.png")
        plt.close()
        
        # Create a summary text file
        with open(f"{output_dir}/summary.txt", 'w', encoding='utf-8') as f:
            f.write("Finnish Churches Statistics\n")
            f.write("==========================\n\n")
            f.write(f"Total churches with valid coordinates: {len(valid_churches)}\n\n")
            f.write("Churches by type:\n")
            for church_type, count in type_counts.items():
                f.write(f"- {church_type}: {count} ({count/len(valid_churches)*100:.1f}%)\n")
        
        print(f"Statistics created in directory: {output_dir}")

def main():
    print("Starting Finnish Churches Visualization")
    print("=======================================")
    
    # First try to use the combined file
    input_file = 'output/all_churches_with_coordinates.json'
    
    # If combined file doesn't exist, try using just the Catholic churches file
    if not os.path.exists(input_file):
        input_file = 'output/catholic_churches_with_coordinates.json'
        if not os.path.exists(input_file):
            print(f"Error: Neither all_churches_with_coordinates.json nor catholic_churches_with_coordinates.json found.")
            return
    
    visualizer = ChurchVisualizer(input_file)
    valid_churches = visualizer.create_map()
    
    if valid_churches:
        visualizer.create_statistics()
    
    print("\nVisualization completed!")

if __name__ == "__main__":
    main()
