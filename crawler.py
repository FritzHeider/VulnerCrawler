import json
import os
import aiohttp
import asyncio
import time
import logging
import signal
import sys
from urllib.parse import urlparse, urljoin
from lxml import html as lh
import argparse

# Configure logging
logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define colors for different log levels
LOG_COLORS = {
    "INFO": "\033[94m",  # Blue
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "DEBUG": "\033[92m",  # Green
    "RESET": "\033[0m"  # Reset
}

# Global variables
visited_urls = set()
max_depth = 3  # Maximum recursion depth

async def main(domain):
    connector = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=connector) as client:
        starting_url = "https://" + domain if not domain.startswith("https://") else domain
        print("Starting crawl at:", starting_url)
        await crawl(client, starting_url, 0)
        sensitive_directories = await get_sensitive_directories(client, starting_url)
        print("Sensitive directories found:", sensitive_directories)

async def crawl(client, url, depth):
    color = LOG_COLORS["INFO"]
    logger.info(f"{color}Analyzing URL: {url}{LOG_COLORS['RESET']}")
    if depth <= max_depth and url not in visited_urls:
        visited_urls.add(url)
        try:
            async with client.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    if html_content:
                        tree = lh.fromstring(html_content)
                        forms = tree.xpath('//form')
                        input_texts = tree.xpath('//input[@type="text"]')
                        if forms or input_texts:
                            logger.info(f"Scrape Found: {url}")
                        internal_links = get_internal_links(url, html_content)
                        print(f"Crawling from {url}: found {len(internal_links)} internal links.")
                        await asyncio.gather(*[crawl(client, link, depth + 1) for link in internal_links])
                        await check_external_resources(client, url, html_content)
                        scraped_data = scrape_data(url, html_content)
                        if scraped_data:
                            logger.info(f"Scraped data from {url}: Title - {scraped_data['Title']}, Paragraphs count - {len(scraped_data['Paragraphs'])}")
                            export_to_json(scraped_data, f"{url.replace(':', '_').replace('/', '_')}.json")
                await asyncio.sleep(1)  # Simple rate limiting
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")

async def access_ipinfo_api(url):
    color = LOG_COLORS["INFO"]
    logger.info(f"{color}Working with IPinfo API...{LOG_COLORS['RESET']}")
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        ipinfo_url = f"http://ip-api.com/json/{domain}"
        async with aiohttp.ClientSession() as session:
            async with session.get(ipinfo_url) as response:
                data = await response.json()
                logger.info(f"IPinfo data for {url}: {data}")
    except Exception as e:
        logger.error(f"Error accessing IPinfo API: {e}")

async def get_sensitive_directories(client, url):
    color = LOG_COLORS["INFO"]
    logger.info(f"{color}Searching for sensitive directories...{LOG_COLORS['RESET']}")
    sensitive_directories = [
        ".git", ".svn", ".DS_Store", "CVS", "backup", "backups", "backup_files", "backup_files_old", "backup_old",
        "backup_old_versions", "old", "old_versions", "old_files", "test", "tests", "temp", "tmp", "logs", "log",
        "debug", ".env"
    ]
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    results = []
    for directory in sensitive_directories:
        test_url = f"{base_url}/{directory}"
        async with client.get(test_url) as response:
            if response.status == 200:
                results.append(test_url)
    return results

async def check_external_resources(client, url, html_content):
    color = LOG_COLORS["INFO"]
    logger.info(f"{color}Checking external resources...{LOG_COLORS['RESET']}")
    tree = lh.fromstring(html_content)
    external_resources = {
        "JavaScript": tree.xpath('//script/@src'),
        "CSS": tree.xpath('//link[@rel="stylesheet"]/@href'),
        "Images": tree.xpath('//img/@src'),
        "Other": tree.xpath('//source/@src') + tree.xpath('//video/@src') + tree.xpath('//audio/@src')
    }
    for resource_type, resources in external_resources.items():
        if resources:
            logger.info(f"{resource_type} resources found on {url}: {resources}")

def get_internal_links(url, html_content):
    tree = lh.fromstring(html_content)
    internal_links = tree.xpath('//a/@href')
    return [urljoin(url, link) for link in internal_links]

def scrape_data(url, html_content):
    color = LOG_COLORS["INFO"]
    logger.info(f"{color}Scraping data from {url}...{LOG_COLORS['RESET']}")
    try:
        tree = lh.fromstring(html_content)
        title = tree.xpath('//title/text()')[0].strip() if tree.xpath('//title/text()') else ""
        paragraphs = [p.strip() for p in tree.xpath('//p/text()') if p.strip()]
        form_links = tree.xpath('//form/@action')
        return {"Title": title, "Paragraphs": paragraphs, "Form Links": form_links}
    except Exception as e:
        logger.error(f"Error scraping data from {url}: {e}")
        return None

def export_to_json(data, filename):
    color = LOG_COLORS["INFO"]
    logger.info(f"{color}Data exported to {filename}{LOG_COLORS['RESET']}")
    with open(filename, "w") as f:
        json.dump(data, f)

def handle_interrupt(signal, frame):
    color = LOG_COLORS["WARNING"]
    logger.warning(f"{color}Program interrupted by user. Exiting...{LOG_COLORS['RESET']}")
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("domain", type=str, help="Enter the domain you want to crawl (e.g., example.com)")
    args = parser.parse_args()
    signal.signal(signal.SIGINT, handle_interrupt)
    start_time = time.time()
    asyncio.run(main(args.domain))
    end_time = time.time()
    execution_time = round(end_time - start_time, 2)
    color = LOG_COLORS["INFO"]
    logger.info(f"{color}Execution time: {execution_time} seconds{LOG_COLORS['RESET']}")
