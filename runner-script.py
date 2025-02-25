# run_extractor.py
from coordinate_extractor import CoordinateExtractor

def main():
    print("Starting Finnish Churches Coordinate Extraction")
    print("==============================================")
    
    # Process Catholic churches
    print("\nProcessing Catholic churches...")
    catholic_extractor = CoordinateExtractor(
        input_file='output/catholic_churches.json',
        output_file='output/catholic_churches_with_coordinates.json'
    )
    catholic_extractor.process_churches()
    
    # Uncomment these sections if you want to process other church types as well
    '''
    # Process Orthodox churches
    print("\nProcessing Orthodox churches...")
    orthodox_extractor = CoordinateExtractor(
        input_file='output/orthodox_churches.json',
        output_file='output/orthodox_churches_with_coordinates.json'
    )
    orthodox_extractor.process_churches()
    
    # Process Lutheran churches
    print("\nProcessing Lutheran churches...")
    lutheran_extractor = CoordinateExtractor(
        input_file='output/lutheran_churches.json',
        output_file='output/lutheran_churches_with_coordinates.json'
    )
    lutheran_extractor.process_churches()
    '''
    
    print("\nCoordinate extraction completed!")

if __name__ == "__main__":
    main()
