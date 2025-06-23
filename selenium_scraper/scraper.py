# Sources - Udemy: Web Scraping in Python Selenium, Scrapy by Frank Andrade
# ANOTHER NOTE: DO NOT USE, GOES AGAINST TARGET ToS
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import pandas as pd # Difference between dumping into a dataframe vs using SQL?

def lambda_handler(event, context):
    # Create a headless environment to run Chrome
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Path to chromedriver executable
    path = '/Users/danicajew/Documents/Side Projects/cut-the-cart/chromedriver-mac-x64/chromedriver'
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service, options=options)

    # Website to scrape
    website = 'https://www.target.com/c/grocery/-/N-5xt1a'

    # Get search query
    search_query = "milk"
    if event and 'search_query' in event:
        search_query = event['search_query']

    products = []

    try:
        driver.get(website)
        print(driver.title)

        # Extract searchbar elements
        search_bar_xpath = '//input[@type="search"]'
        search_button_xpath = '//button[@aria-label="search"]'

        # Wait for the search bar to be visible, then type the query
        wait = WebDriverWait(driver, 10)
        search_bar = wait.until(EC.visibility_of_element_located((By.XPATH, search_bar_xpath)))

        search_bar.clear()
        search_bar.send_keys(search_query)

        driver.find_element(By.XPATH, search_button_xpath).click()

        # Look through product cards and store product data
        product_card_xpath = '//div[@data-test="@web/ProductCard/ProductCardVariantDefault"]'
        wait.until(EC.presence_of_all_elements_located((By.XPATH, product_card_xpath)))
        product_elements = driver.find_elements(By.XPATH, product_card_xpath)

        for element in product_elements:
            try:
                # Use a relative XPath (starting with '.') to search within the product card element
                name_xpath = ".//a[@data-test='product-title']"
                price_xpath = './/*[@data-test="current-price"]//span'
                # Can find the comparison xpaths later?
                
                name = element.find_element(By.XPATH, name_xpath).text
                price = element.find_element(By.XPATH, price_xpath).text
                print(f"Current product: {name} ---- ${price}")
                products.append({"name": name.rstrip(), "price": price.rstrip()})
            except Exception as e:
                print(f"Error scraping a product element: {e}")

        time.sleep(30)
    except Exception as e:
        print("Error occurred while operating driver:", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        driver.quit()
    
    return {
        'statusCode': 200,
        'body': json.dumps(products, indent=4) # Using indent for pretty printing
    }


# Testing
if __name__ == '__main__':
    # Simulate an event dictionary to pass a search query for local testing
    mock_event = {'search_query': 'cereal'} 
    
    result = lambda_handler(mock_event, None)
    print(result)