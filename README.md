# VulnerCrawler
Python Web Crawler
This Python web crawler is designed to systematically index the content of web pages from a specified domain. It uses asynchronous programming to efficiently handle multiple web requests and parse data. The crawler extracts data such as page titles, paragraphs, and form actions, and it identifies internal links to continue the crawling process recursively. Additionally, it checks for sensitive directories and gathers external resources linked within the pages.

Features
Asynchronous Web Crawling: Fast and efficient crawling using aiohttp and asyncio.
Data Extraction: Scrapes titles, paragraphs, and form actions from web pages.
Sensitive Directory Detection: Checks for directories that commonly contain sensitive information.
External Resource Identification: Lists JavaScripts, CSS files, images, and other resources included in web pages.
Rate Limiting: Simple delay implementation to prevent hitting servers too aggressively.
Command Line Interface: Easy to use with command line arguments for specifying the target domain.
Robust Error Handling: Gracefully handles network issues and HTML parsing errors.
Logging and User Feedback: Color-coded logging and real-time progress updates on the terminal.
Prerequisites
Before you start using the crawler, ensure you have Python 3.7+ installed on your system. Additionally, you need the following packages:

aiohttp
lxml
argparse
You can install these with pip:

bash
Copy code
pip install aiohttp lxml argparse
Usage
To use the crawler, navigate to the directory containing the script and run it with the domain you want to crawl:

bash
Copy code
python web_crawler.py example.com
Replace example.com with the domain you wish to crawl. The script will start crawling from the root of this domain.

Output
The script logs its progress and results directly to the terminal. It uses different colors for various log levels to make the output easier to read:

Blue: Information
Yellow: Warnings
Red: Errors
Green: Debugging information
Scraped data is saved in JSON format in the current directory, with filenames corresponding to the URLs from which the data was extracted.

Safety and Compliance
This tool is intended for ethical use, such as penetration testing, academic research, or SEO analysis. Users are responsible for ensuring they have permission to crawl and test websites and that they comply with any relevant laws and terms of service.

Interrupting the Crawler
To stop the crawler gracefully, press CTRL+C. The program will catch the interrupt signal and terminate cleanly, providing a summary of its runtime.

Contributing
Contributions to improve the crawler are welcome. Please feel free to fork the repository, make changes, and submit a pull request.

