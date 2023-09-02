import re
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
from validate_email import validate_email

class WebScraper:
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.unprocessed_urls = deque([starting_url])
        self.processed_urls = set()
        self.emails = set()
        self.social_links = set()
        self.base_domain = urlsplit(starting_url).netloc

    def crawl(self):
        while self.unprocessed_urls:
            url = self.unprocessed_urls.popleft()
            self.processed_urls.add(url)
            parts = urlsplit(url)
            base_url = f"{parts.scheme}://{parts.netloc}"
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url

            try:
                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                continue

            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
            self.emails.update(email for email in new_emails if validate_email(email))

            soup = BeautifulSoup(response.text, 'lxml')

            for anchor in soup.find_all("a"):
                link = anchor.attrs["href"] if "href" in anchor.attrs else ''

                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = path + link

                if self.base_domain in link:
                    if link not in self.unprocessed_urls and link not in self.processed_urls:
                        if re.match(r"(?:https?:\/\/)?(?:www\.)?(facebook|twitter|instagram)\.com\/[^\/\s]+", link):
                            self.social_links.add(link)
                        else:
                            if ("contact" in link or "Contact" in link or "About" in link or "about" in link or 'CONTACT' in link or 'ABOUT' in link or 'contact-us' in link):
                                self.unprocessed_urls.append(link)
                            else:
                                self.unprocessed_urls.append(link)


# Usage
if __name__ == "__main__":
    scraper = WebScraper('https://coursee.org/article/what-is-machine-learning-and-what-are-its-uses')
    scraper.crawl()
    print("Emails:", scraper.emails)
    print("Social Links:", scraper.social_links)
