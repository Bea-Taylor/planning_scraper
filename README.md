# Planning scraper 

This is open source code for web-scraping information about planning applications from local authority district planning portal websites. It automates the collection of digital information that is in the public domain. 

## Running the code 

You can install all the dependencies you need using the requirments.yml and a conda env. 

Through experimentation, I've discovered that Selenium and ChromeDriver is the best way to run this code. The code has lots of timed breaks built in to minimise the chance of crashing the websites server. 

### Tips 
Personally I run the scripts from a remote server, and save the data to a remote database. 

You don't need to run it from a remote server, but you will want to run it continously for a while - Linux screen is your friend here! 

## Examples 

There is an example of how to run the code in the Jupyter notebook: `example_scraping.ipynb'. 

## Credit

If you use my code please cite it! 
