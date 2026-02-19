# Planning Scraper 

A lightweight Python module for scraping planning application data from local planning authority websites, automating the collation of digital information in the public domain. 

## Set-up 

There are three simple steps to get the repo up and running!

1. Clone/download the repository
2. Install requirements

### Install dependencies
**Conda (preferred):**
```bash
conda env create -f environment.yml
conda activate web_scrape_env
```
The virtual environment ensures you have the right Selenium and ChromeDriver packages installed - these are necessary for the webscraping. 

### Install ChromeDriver
**macOS:**
```bash
brew install chromedriver
```

3. Import from the `planning_scraper/` directory

## Usage

There is an example of how to run the code in the Jupyter notebook: `example_scraping.ipynb'. 

## Project architecture

```
planning-scraper/
├── README.md
├── requirements.txt
├── example_scraping.ipynb
├── .gitignore
│
├── planning_scraper/
│   ├── __init__.py
│   ├── driver.py          # WebDriver setup
│   ├── scraper.py         # Main scraping functions
│   ├── utils.py           # Helper utilities
│   └── geolocator.py      # Address processing
│
└── data/
    ├── input/
    │   └── example_urls.csv
    └── output/
```

## Functions

### `scraper.py`
Main scraping functions. 

- **`get_postcode_page(council, postcode, os_type="mac")`**
  - Search for all applications in a postcode
  - Returns list of URLs

- **`scrape_app_details(urls, os_type="mac", max_retries=3)`**
  - Scrape details from application URLs
  - Returns dictionary of data

- **`scrape_comments(driver, council, app_id, url, comments_saver=None)`**
  - Scrape comments from an application
  - Returns count of comments

### `geolocator.py`
Address processing and geocoding utilities.

- **`extract_postcode(address)`**
  - Extract UK postcode from address string

- **`parse_address(address_string)`**
  - Parse address into components (street, city, postcode)

- **`clean_address(address)`**
  - Clean and standardise address string

- **`process_address_dataframe(df, address_column='address')`**
  - Process all addresses in a DataFrame

- **`calculate_distance(lat1, lon1, lat2, lon2)`**
  - Calculate distance between coordinates (km)

### `driver.py`
WebDriver setup and configuration.

- **`setup_driver(os_type="mac", headless=True)`**
  - Set up Chrome WebDriver

### `utils.py`
Utility functions for the scraper.

- **`get_council_url(council)`**
  - Get council URL from CSV

- **`check_rate_limit(driver)`**
  - Check if rate limited

- **`is_missing(value)`**
  - Check if value is missing/NaN

- **`get_table_value(driver, label)`**
  - Extract value from HTML table

## Tips 

**Leave the code running**
I've been using this code to scrape comments left on planning applications. I've found the best way to run this code is to provide a dataset of locations (planning refs, postcodes, uprns, addresses etc) - and then get the code to cycle through them - saving the results to a database. The code takes a while to run as it has lots of pauses built in to avoid crashing the host websites. Since  I like to be able to abandon my laptop I've been executing the code from a remote server. I've found [linux screen](https://linuxize.com/post/how-to-use-linux-screen/) really helpful for this. 

**Use Selenium and ChromeDriver**
Through experimentation I've found that Selenium and ChromeDriver are the most effective packages for webscraping. In order to install the correct dependencies I would recommend creating a conda virtual env from the enviornment.yml file supplied. 

**Check the website html**
The code has been designed to automate scraping of council websites which use the idox backend - since this has uniform html formatting. If the planning website you're trying to scrape has a different format you will need to update the code accordingly.

## License
Feel free to use and modify!

Developed by Bea Taylor. I used Claude code to refactor parts of this repo - please create issues/pull requests for any problems - I would appreciate the feedback!  
