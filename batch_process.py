# Osaa ajaa useamman tiedoston kerrallaan ja käyttää CoordinateExtractor-luokkaa koordinaattien poimimiseen.
from coordinate_extractor import CoordinateExtractor
import json
import os

def combine_results(output_file='output/all_churches_with_coordinates.json'):
    """Combine all the individual results into a single JSON file"""
    all_churches = []
    
    # List of potential input files
    input_files = [
        'output/catholic_churches_with_coordinates.json',
        'output/orthodox_churches_with_coordinates.json',
        'output/lutheran_churches_with_coordinates.json'
    ]
    
    # Load and combine all available result files
    for file in input_files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    churches = json.load(f)
                    all_churches.extend(churches)
                    print(f"Added {len(churches)} churches from {file}")
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {file}")
    
    # Save the combined results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_churches, f, ensure_ascii=False, indent=4)
    
    print(f"\nCombined {len(all_churches)} churches into {output_file}")

def main():
    print("Starting Finnish Churches Batch Processing")
    print("==========================================")
    
    # Process all church types
    church_types = [
        {
            "name": "Catholic",
            "input": "output/catholic_churches.json",
            "output": "output/catholic_churches_with_coordinates.json"
        },
        {
            "name": "Orthodox",
            "input": "output/orthodox_churches.json",
            "output": "output/orthodox_churches_with_coordinates.json"
        },
        {
            "name": "Lutheran",
            "input": "output/lutheran_churches.json",
            "output": "output/lutheran_churches_with_coordinates.json"
        }
    ]
    
    for church_type in church_types:
        if os.path.exists(church_type["input"]):
            print(f"\nProcessing {church_type['name']} churches...")
            extractor = CoordinateExtractor(
                input_file=church_type["input"],
                output_file=church_type["output"]
            )
            extractor.process_churches()
        else:
            print(f"\nSkipping {church_type['name']} churches: Input file {church_type['input']} not found.")
    
    # Combine all results
    print("\nCombining all results...")
    combine_results()
    
    print("\nBatch processing completed!")

if __name__ == "__main__":
    main()