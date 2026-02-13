# Planning Scraper 

A modular Python package for scraping planning application data from local authority district planning portal websites, automating the collation of digital information in the public domain. 

## Project Structure

```
pipeline/
├── __init__.py           # Package initialization and exports
├── config.py             # Configuration management and settings
├── browser.py            # Browser setup and WebDriver management
├── navigation.py         # URL navigation and page interactions
├── parsers.py            # HTML parsing and data extraction
├── scraper.py            # Core scraping orchestration
├── utils.py              # Helper functions and utilities
└── geo_locater.py        # Geographic location utilities (existing)
```
## Running the code 

Through experimentation I've found that Selenium and ChromeDriver are the most effective packages for webscraping. In order to install the correct dependencies I would recommend creating a conda virtual env from the requirements.yml file supplied. 

The code has been designed to autmatie scrapign of websites which use the idox backend - which has uniform html formatting. If the plannign website has a different format you will need to update the code accoridngly. To minimise the risk of crashing the websites the code has lots of timed breaks, the does mean that the code takes a little bit longer to run. 

## Architecture

### **browser.py** 
- `setup_driver(os_type, headless)` - Configure and return Chrome WebDriver
- `BrowserManager` - Context manager for automatic cleanup
- `check_rate_limit(driver)` - Detect rate limiting

**Purpose:** All browser/WebDriver configuration and lifecycle management

### **config.py** 
- `Config` class - Centralized configuration
- `get_council_url(council)` - Retrieve council URLs
- `validate_config()` - Validate configuration files

**Purpose:** Configuration management and validation

### **navigation.py** 
- `get_application_page(driver, council, app_id)` - Navigate to application page
- `get_postcode_page(council, postcode)` - Get all URLs for a postcode
- `has_comments(driver, url)` - Check if page has comments
- `build_further_info_url(base_url)` - Generate details page URL
- `build_comments_url(base_url, page_number)` - Generate comments page URL

**Purpose:** All URL navigation and page interaction logic

### **parsers.py**
- `get_table_value(driver, label)` - Extract table cell value
- `parse_application_details(driver)` - Parse main application data
- `parse_further_info(driver)` - Parse additional details
- `get_comments_count(driver)` - Extract comment count

**Purpose:** HTML parsing and data extraction

### **scraper.py**
- `ApplicationScraper` - Main scraper class
- `scrape_app_details(urls)` - Scrape multiple applications
- `scrape_comments(...)` - Scrape comments from application

**Purpose:** High-level scraping orchestration and retry logic

### **utils.py** 
- `retry_with_backoff(func, ...)` - Retry with exponential backoff
- `random_sleep(min, max)` - Sleep random duration
- `sanitize_filename(filename)` - Clean filenames
- `format_postcode(postcode)` - Format UK postcodes
- `validate_app_id(app_id)` - Validate application IDs
- `chunk_list(items, chunk_size)` - Split lists into chunks
- `log_scraping_stats(...)` - Log scraping statistics

**Purpose:** Reusable utility functions

## Usage

There is an example of how to run the code in the Jupyter notebook: `example_scraping.ipynb'. 

### Basic Application Scraping

```python
from pipeline import ApplicationScraper

# Initialize scraper
scraper = ApplicationScraper(os_type="mac", max_retries=3)

# Scrape applications
urls = [
    "https://example.com/application/123",
    "https://example.com/application/456"
]

data = scraper.scrape_app_details(urls)

# Convert to DataFrame
import pandas as pd
df = pd.DataFrame(data)
```

### Using Context Manager for Browser

```python
from pipeline import BrowserManager, get_application_page

with BrowserManager(os_type="mac") as driver:
    url = get_application_page(driver, "Westminster", "APP-001")
    print(f"Application URL: {url}")
```

### Postcode Search

```python
from pipeline import get_postcode_page

# Get all applications for a postcode
urls = get_postcode_page("Westminster", "SW1A 1AA")
print(f"Found {len(urls)} applications")
```

### Checking for Comments

```python
from pipeline import BrowserManager, has_comments

with BrowserManager() as driver:
    if has_comments(driver, application_url):
        print("This application has comments")
```

### Scraping Comments

```python
from pipeline import ApplicationScraper, BrowserManager

scraper = ApplicationScraper()

with BrowserManager() as driver:
    num_comments = scraper.scrape_comments(
        driver=driver,
        council="Westminster",
        app_id="APP-001",
        application_url="https://example.com/app/summary",
        comments_saver=None  # Or pass CommentsSaver instance
    )
    print(f"Scraped {num_comments} comments")
```

## Configuration

The package expects a CSV file at `data/input/example_urls.csv` with council URLs:

```csv
council,url
westminster,https://idoxpa.westminster.gov.uk/online-applications
camden,https://opendata.camden.gov.uk/...
```

### Customizing Configuration

```python
from pipeline.config import Config

# Change default settings
Config.DEFAULT_WAIT_TIMEOUT = 15
Config.MAX_RETRIES = 5
Config.RATE_LIMIT_SLEEP = 600  # 10 minutes
```

## Testing

Each module can be tested independently:

```python
# Test browser setup
from pipeline.browser import setup_driver
driver = setup_driver("mac")
assert driver is not None
driver.quit()

# Test parsers
from pipeline.parsers import parse_application_details
with BrowserManager() as driver:
    driver.get(url)
    details = parse_application_details(driver)
    assert "reference" in details
```

## Tips 
I've been using this code to scrape comments lef ton planning applictaiopns. I'cve foudn the best way to run this code is to provide a datraset of locaitons (planing refs, psotcode, uprns, addresses etc) - and then get the code to cycle through them - saving the results ot a database. I've found the best way to do this us by running the scripts form a remotve server. You don't need to run it from a remote server, but you will want to run it continously for a while - Linux screen is your friend here! 

-----------

Developed by Bea Taylor and AI4CI. 

