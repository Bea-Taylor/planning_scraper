# Planning Scraper 

This code provides a pipeline to web-scrape information from local authority district planning portal websites, automating the collation of digital information in the public domain. 

## Running the code 

Through experimentation I've found that Selenium and ChromeDriver are the most effective packages for webscraping. In order to install the correct dependencies I would recommend creating a conda virtual env from the requirements.yml file supplied. 

The code has been designed to autmatie scrapign of websites which use the idox backend - which has uniform html formatting. If the plannign website has a different format you will need to update the code accoridngly. To minimise the risk of crashing the websites the code has lots of timed breaks, the does mean that the code takes a little bit longer to run. 

### Tips 
I've been using this code to scrape comments lef ton planning applictaiopns. I'cve foudn the best way to run this code is to provide a datraset of locaitons (planing refs, psotcode, uprns, addresses etc) - and then get the code to cycle through them - saving the results ot a database. I've found the best way to do this us by running the scripts form a remotve server. You don't need to run it from a remote server, but you will want to run it continously for a while - Linux screen is your friend here! 

## Examples 

There is an example of how to run the code in the Jupyter notebook: `example_scraping.ipynb'. 

-----

Developed by Bea Taylor and AI4CI. 
