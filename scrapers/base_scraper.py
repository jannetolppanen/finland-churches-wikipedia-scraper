import requests
from bs4 import BeautifulSoup

class BaseScraper:
    def __init__(self, url, church_type):
        self.url = url
        self.church_type = church_type
    
    def fetch_page(self):
        response = requests.get(self.url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    
    def get_churches(self):
        """To be implemented by subclasses"""
        raise NotImplementedError