# scrapers/lutheran_scraper.py
from scrapers.base_scraper import BaseScraper
import re

class LutheranScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            "https://fi.wikipedia.org/wiki/Luettelo_Suomen_luterilaisista_kirkoista",
            "Lutheran"
        )

    def clean_church_name(self, name):
        """
        Clean the church name by removing any trailing numbers enclosed in brackets.
        """
        # Updated regex to match multiple occurrences of bracketed numbers
        return re.sub(r'\s*\[\d+\]', '', name).strip()
    
    def get_churches(self):
        soup = self.fetch_page()
        churches = []
        skipped_count = 0
        
        # Find the table with class "wikitable sortable"
        table = soup.find('table', class_='wikitable sortable')
        
        if table:
            # Skip the header row
            rows = table.find_all('tr')[1:]
            
            print(f"Processing Lutheran churches table with {len(rows)} rows")
            
            for row in rows:
                # Get all cells in the row
                cells = row.find_all('td')
                
                if cells:
                    # The first cell contains the church name and link
                    name_cell = cells[0]
                    link = name_cell.find('a')
                    
                    # Get the name regardless of whether there's a valid link
                    name = name_cell.get_text().strip()
                    
                    if link:
                        # Check if the link is a "redlink" (points to a non-existent page)
                        href = link.get('href', '')
                        link_class = link.get('class', [])
                        is_redlink = 'redlink=1' in href or 'new' in link_class
                        
                        if not is_redlink:
                            wiki_link = "https://fi.wikipedia.org" + href

                            # Clean the church name
                            name = self.clean_church_name(name)
                            
                            # Create church entry with just the basic info
                            church = {
                                "name": name,
                                "type": self.church_type,
                                "wikipedia_link": wiki_link,
                                "coordinates": {}  # Empty placeholder for now
                            }
                            
                            churches.append(church)
                        else:
                            print(f"Skipping church with redlink: {name}")
                            skipped_count += 1
                    else:
                        print(f"Skipping church with no link: {name}")
                        skipped_count += 1
        else:
            print("Warning: Could not find the Lutheran churches table!")
        
        print(f"Total Lutheran churches processed: {len(churches)}")
        print(f"Total Lutheran churches skipped: {skipped_count}")
        
        return churches