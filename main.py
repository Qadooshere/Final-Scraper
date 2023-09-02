import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import random


class GoogleScraper:
    BASE_URL = 'https://www.google.com/search'

    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'cookie': '...'  # Specify your cookies here
        }

    def fetch(self, query, page=0, country='us', language='en'):
        params = self._get_params(query, page, country, language)
        response = self._make_request(params)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch results. Status code: {response.status_code}")
            return None

    def _get_params(self, query, page, country, language):
        if page == 0:
            return {
                'q': query,
                'start': '0',
                'gl': country,
                'hl': language
            }
        else:
            return {
                'q': query,
                'start': str(page * 10),
                'gl': country,
                'hl': language
            }

    def _make_request(self, params):
        try:
            self.headers['User-Agent'] = self.ua.random
            response = self.session.get(self.BASE_URL, params=params, headers=self.headers)
            print(f'HTTP GET request to URL: {response.url} | Status code: {response.status_code}')
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None

    def extract_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.select('.yuRUbf')
        processed_data = []
        for result in results:
            title = result.select_one('h3').get_text()
            link = result.select_one('a')['href']
            processed_data.append({'title': title, 'link': link})
        return processed_data

    def scrape_generator(self, query, num_pages=1, country='us', language='en'):
        for page in range(num_pages):
            page_html = self.fetch(query, page, country, language)
            if not page_html:
                break

            page_results = self.extract_links(page_html)
            yield page_results

            time.sleep(random.uniform(2, 4))

