import json
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys    # type things in the search bar and see the results

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Create a Chrome browser instance and enable headless mode
options = Options()
options.add_argument('--headless')  # 启用无头模式


# ...
# Code for page access and data extraction
# ...

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from lxml import etree
import urllib.parse
from review_spider import get_max_page, organize_info, scrap_review
import os
from fuzzywuzzy import fuzz
#```

is_all_reviews_from_this_business = True


PATH = '/Users/fangzheng/Downloads/archive/yelp_academic_dataset_business.json'
# read data in the json file
data = pd.read_json(PATH, lines=True)

print(data)
store_name_list = data['name']
city_list  = data['city']
address_list = data['address']
# driver = webdriver.Chrome(options=options )
driver = webdriver.Chrome( )

no_results_index = [11,13]
counter = 0
selected_url = ""

# counter = 314
# store_name_list, city_list, address_list = store_name_list[counter:], city_list[counter:], address_list[counter:]

def check_top_match(check_):
    for i in check_:
        if i.text == 'Top match':
            print('has Top Match')
            # counter += 1
            return True
    return False
for store_name, city,address in zip(store_name_list, city_list, address_list):
    print(counter)
    city_address_encoded = urllib.parse.quote(city+' '+address)
    store_name_encoded = urllib.parse.quote(store_name)
    
    URL = 'https://www.yelp.com/search?find_desc={}&find_loc={}'.format(store_name_encoded, city_address_encoded)
    print(URL)
    driver.get(URL)
    find_top_match = driver.find_elements(By.XPATH,'//h2[contains(@class,"css-agyoef") and (text()="Top match" or text()="Top matches")]')

    if len(find_top_match) == 0:
        # no top match

        check_element = driver.find_elements(By.XPATH, '//div[contains(@class,"arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG css-1qn0b6x")]/h1[contains(@class,"css-oxqmph")]/span[contains(@class," raw__09f24__T4Ezm")]')
        check_sorry_results = driver.find_elements(By.XPATH,'//li[contains(@class," css-1qn0b6x")]/div[contains(@class,"message__09f24__vXpJu css-179clo6")]/div[contains(@class," css-174a15u")]/h2[contains(@class,"css-e29med")]')
    
        if (check_element and "No results for" in check_element[0].text) or (check_sorry_results and "Sorry, we couldn't find any results" in check_sorry_results[0].text):
            print("No results found.")
            no_results_index.append(counter)

        else:
            print("Results found. Proceed with scraping...")
            selected_url = ""
            name_elements = driver.find_elements(By.XPATH,f'//div[contains(@class," css-1qn0b6x")]/h3[contains(@class,"css-1agk4wl")]/span[contains(@class," css-1egxyvc")]/a[contains(@class,"css-19v1rkv")]')
            
            for i in name_elements:
                # if (i.text.replace("'",'"')) == (store_name) : Because Kengdao's webpage is in Chinese, but the database is in English, so we need to convert it here
                # Use a string similarity algorithm to measure the similarity between two strings.
                # One commonly used algorithm is the Levenshtein distance, which can calculate the editing distance between two strings, that is, how many insertion, deletion, or replacement operations need to be performed to convert one string to another.
                if fuzz.ratio(i.text, store_name)>87:
                    print('has this store')
                    selected_url = i.get_attribute('href')
                    print(selected_url)
                    break

                # print(i.text)
            if len(selected_url) != 0:
                all_reviews_from_this_business = scrap_review(selected_url)
                if len(all_reviews_from_this_business) == 0:
                    print('no reviews found')
                    continue
            else:
                print('no store found')
                is_all_reviews_from_this_business = False
                continue
            directory = 'reviews'
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open('reviews/'+str(counter)+'.json', 'w') as f:
                json.dump(all_reviews_from_this_business, f)
            print()

        # pass
    else:
        # has top match, find the next 
        a_elements = driver.find_elements(By.XPATH,'//ul[contains(@class, "undefined list__09f24__ynIEd")]/li[contains(@class, "css-1qn0b6x") and div/h2[contains(@class, "css-agyoef") and text() = "Top match"]]/following-sibling::li[1]//div[contains(@class," css-1qn0b6x")]/h3[contains(@class,"css-1agk4wl")]/span[contains(@class," css-1egxyvc")]/a[contains(@class,"css-19v1rkv")]')
        if len(a_elements) == 0:
            pass
        else:
            selected_url = a_elements[0].get_attribute('href')
            print(selected_url)
            all_reviews_from_this_business = scrap_review(selected_url)
            directory = 'reviews'
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open('reviews/'+str(counter)+'.json', 'w') as f:
                json.dump(all_reviews_from_this_business, f)
            print()


    counter += 1
    if is_all_reviews_from_this_business != False:
        all_reviews_from_this_business.clear()
    continue
  
driver.quit()