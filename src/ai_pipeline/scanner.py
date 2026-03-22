import os
import requests
import multiprocessing as mp

class ScrapeSwarm:
    def __init__(self, urls, num_workers):
        self.urls = urls
        self.num_workers = num_workers
        self.results = []

    def scrape_url(self, url):
        try:
            response = requests.get(url)
            return response.text
        except:
            return None

    def run(self):
        pool = mp.Pool(processes=self.num_workers)
        self.results = pool.map(self.scrape_url, self.urls)
        pool.close()
        pool.join()
        return self.results

if __name__ == '__main__':
    urls = ['https://example.com', 'https://another-example.org', 'https://third-example.net']
    swarm = ScrapeSwarm(urls, num_workers=4)
    results = swarm.run()
    for result in results:
        if result:
            print(result)
        else:
            print('Error scraping url')