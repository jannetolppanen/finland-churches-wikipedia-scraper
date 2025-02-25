# scrapers/orthodox_scraper.py
from scrapers.base_scraper import BaseScraper

class OrthodoxScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            "https://fi.wikipedia.org/wiki/Luettelo_Suomen_ortodoksisista_kirkoista",
            "Orthodox"
        )
    
    def get_churches(self):
        soup = self.fetch_page()
        churches = []
        skipped_count = 0
        
        # Find the tables with class "wikitable sortable"
        tables = soup.find_all('table', class_='wikitable sortable')
        
        print(f"Found {len(tables)} tables of churches")
        
        table_num = 1
        for table in tables:
            # Skip the header row
            rows = table.find_all('tr')[1:]
            
            print(f"Processing table {table_num} with {len(rows)} rows")
            table_num += 1
            
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
        
        print(f"Total churches processed: {len(churches)}")
        print(f"Total churches skipped: {skipped_count}")
        
        return churches