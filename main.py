# main.py for initial scraping and saving to JSON files
import json
import os
from scrapers.catholic_scraper import CatholicScraper
from scrapers.orthodox_scraper import OrthodoxScraper
from scrapers.lutheran_scraper import LutheranScraper

def main():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Initialize scrapers
    catholic_scraper = CatholicScraper()
    orthodox_scraper = OrthodoxScraper()
    lutheran_scraper = LutheranScraper()
    
    # Get churches from each source
    catholic_churches = catholic_scraper.get_churches()
    orthodox_churches = orthodox_scraper.get_churches()
    lutheran_churches = lutheran_scraper.get_churches()
    
    # Save to individual JSON files
    with open('output/catholic_churches.json', 'w', encoding='utf-8') as f:
        json.dump(catholic_churches, f, ensure_ascii=False, indent=4)
    
    with open('output/orthodox_churches.json', 'w', encoding='utf-8') as f:
        json.dump(orthodox_churches, f, ensure_ascii=False, indent=4)
    
    with open('output/lutheran_churches.json', 'w', encoding='utf-8') as f:
        json.dump(lutheran_churches, f, ensure_ascii=False, indent=4)
    
    # Combine all churches
    all_churches = catholic_churches + orthodox_churches + lutheran_churches
    
    # Save to combined JSON file
    with open('output/all_churches.json', 'w', encoding='utf-8') as f:
        json.dump(all_churches, f, ensure_ascii=False, indent=4)
    
    print("\nSummary:")
    print(f"- Catholic churches: {len(catholic_churches)}")
    print(f"- Orthodox churches: {len(orthodox_churches)}")
    print(f"- Lutheran churches: {len(lutheran_churches)}")
    print(f"- Total: {len(all_churches)} churches")

if __name__ == "__main__":
    main()