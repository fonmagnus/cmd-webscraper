__all__ = ['Scraper']
import requests
import threading, os
import sqlite3, json
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from .repository import Repository

class Scraper:
    def __init__(self, *args, **kwargs):
        self.urls = kwargs.get('urls', [])
        self.metadata = kwargs.get('metadata', None)
        self.save_assets = kwargs.get('save_assets', False)
        self.repository = Repository()
        self.errors = []
        self.error_lock = threading.Lock()
    #end def

    def run(self):
        if self.urls is not None and len(self.urls) > 0:
            self.scrap()
        elif self.metadata is not None:
            self.load_metadata()
        #end if
    #end def

    def scrap(self):
        scrap_threads = []
        for url in self.urls:
            thread = threading.Thread(target=self.scrap_page, args=(url,))
            scrap_threads.append(thread)
            thread.start()
        #end for
        
        for thread in scrap_threads:
            thread.join()
        #end for
        print('Done scraping')
        for error in self.errors:
            print(f'Error scraping {error[0]}: {error[1]}')
    #end def
        
    def scrap_page(self, url: str):
        try:
            page_contents = self.get_page_contents(url)
            self.save_page_contents(page_contents, url)
        except Exception as e:
            with self.error_lock:
                self.errors.append((url, e))
            #end with    
        #end try
    #end def
            
    def get_page_contents(self, url: str) -> Dict[str, Any]:
        print(f'Scraping web URL from {url}')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return {
            'title': self._get_title(url),
            'content': soup,
        }
    #end def

    def save_page_contents(self, page: Dict[str, Any], url: str):
        title = page.get('title', 'untitled')
        safe_title = self._get_safe_title(title)
        content = page.get('content', '')
        os.makedirs(f'scraped_pages/{safe_title}', exist_ok=True)

        with open(f'scraped_pages/{safe_title}/{safe_title}.html', 'w') as file:
            file.write(content.prettify())
        #end with
        self.save_page_metadata(title, page, url)
    #end def
        
    def save_page_metadata(self, title: str, page: Dict[str, Any], url: str):
        attributes = self._get_html_attributes(page.get('content'), url, title)
        self.repository.save_to_sqlite_driver(title, attributes)
    #end def
            
    def load_metadata(self):
        result = self.repository.load_metadata(self.metadata)
        if result == None:
            self.scrap_page(self.metadata)
            result = self.repository.load_metadata(self.metadata)
        #end if
        self.print_metadata(
            result.get('title', ''),
            result.get('attributes', '{}'),
            result.get('created_at', '')
        )
    #end def

    def print_metadata(self, title, attributes: str, created_at: str) -> Dict[str, Any]:
        attributes = json.loads(attributes)
        print(f'site: {title}')
        print(f'number of links: {len(attributes.get("links", []))}')
        print(f'number of images: {len(attributes.get("images", []))}')
        print(f'last fetch: {datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f").strftime("%a %b %d %Y %H:%M %Z UTC")}')
        if self.show_full_links:
            print('links:')
            for link in attributes['links']:
                print(link)
            #end for
        #end if
        if self.show_full_images:
            print('images:')
            for image in attributes['images']:
                print(image)
            #end for
        #end if
    #end def

    # * private methods
    def _get_title(self, url: str) -> str:
        if url is None:
            return "untitled"
        return url
    #end def

    def _get_safe_title(self, title: str) -> str:
        safe_title = title.replace('/', '_').replace(':', '_')
        return safe_title
    #end def
    
    def _get_html_attributes(self, soup: BeautifulSoup, url: str, title: str) -> Dict[str, Any]:
        link_attributes = ['a']
        image_attributes = ['img']
        attributes = {
            'links': [],
            'images': []
        }

        for tag in soup.descendants:
            if tag.name in link_attributes:
                attributes['links'].append(tag.get('href', '#'))
            elif tag.name in image_attributes:
                attributes['images'].append(tag.get('src', '#'))
            #end if
        #end for
        if self.save_assets:
            self._save_assets(soup, url, title)
        #end if
        return attributes
    #end def

    def _get_url(self, tag, base_url: str) -> str:
        url = tag.get('src') or tag.get('href')
        if url and url.startswith('//'):
            url = 'https:' + url
        elif url and not url.startswith('http'):
            url = urljoin(base_url, url)
        #end if
        return url
    #end def

    def _download_file(self, url, filename) -> None:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
                #end for
            #end with
        else:
            print(response)
            print(f'Error downloading {url}: {response.status_code}')
        #end if
    #end def

    def _save_assets(self, soup: BeautifulSoup, base_url: str, title: str) -> List[str]:
        title = self._get_safe_title(title)
        assets = []
        for tag in soup.find_all(['img', 'link', 'script']):
            url = self._get_url(tag, base_url)
            if url:
                print('Downloading assets from', url)
                try:
                    if url.startswith('http'):
                        split_url = url.split('://')[-1].split('/', 1)
                        domain = split_url[0]
                        path = split_url[1] if len(split_url) > 1 else ''
                        filename = os.path.join(domain, path.replace('/', os.sep))
                        directory = os.path.join('scraped_pages', title)
                        filename = os.path.join(directory, filename)
                        if '.' in os.path.basename(filename):
                            self._download_file(url, filename)
                            assets.append(filename)
                        #end if
                    #end if
                except Exception as e:
                    print(f"Error downloading {url}: {e}")
                #end try
            #end if
        #end for
        return assets
    #end def
#end class
            
