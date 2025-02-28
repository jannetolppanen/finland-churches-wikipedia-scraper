# scrapers/catholic_scraper.py
from scrapers.base_scraper import BaseScraper
import re

class CatholicScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            "https://fi.wikipedia.org/wiki/Luettelo_Suomen_katolisista_kirkoista",
            "Catholic"
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

        # Find the table with class "wikitable sortable"
        table = soup.find('table', class_='wikitable sortable')

        if table:
            # Skip the header row
            rows = table.find_all('tr')[1:]

            for row in rows:
                # Get all cells in the row
                cells = row.find_all('td')

                if cells:
                    # The first cell contains the church name and link
                    name_cell = cells[0]
                    link = name_cell.find('a')

                    if link:
                        # Check if the link is a "redlink" (points to a non-existent page)
                        is_redlink = 'redlink=1' in link.get('href') or 'new' in link.get('class', [])

                        if not is_redlink:
                            name = link.text.strip()
                            wiki_link = "https://fi.wikipedia.org" + link.get('href')

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
                            # Optionally, print a message about skipping a redlink
                            print(f"Skipping church with no Wikipedia page: {link.text.strip()}")

        return churches

