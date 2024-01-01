from selenium import webdriver
from selenium.webdriver.common.keys import Keys    # type things in the search bar and see the results

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from lxml import etree
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

options = Options()
options.add_argument('--headless')  # 启用无头模式


# PATH = '..../..../chromedriver'
PATH = '/Users/fangzheng/Downloads/chromedriver_mac_arm64/chromedriver'
from selenium.webdriver.chrome.options import Options   # 实现无可视化界面


def get_max_page(element):
    """
    Function: Get the total page number of reviews, for further click iteration.
    parser:   HTML page
    """

    # Get the text within the element
    text = element.text 
    # Split the text to get the number of reviews
    text = text.split(' ')
    # Get the number of reviews
    count = int(text[-1])
    return count


def organize_info(info):
    """ 
    Utility Function.
    Since each time we return lists of dictionaries, 
    this function is for concatenating all dictionaries into one single list.
    """
    final_info = []
    for i in info:
        for j in i:
            final_info.append(j)
    return final_info


def scrap_review(url):
    """
    Function: Scrap reviews of one restaurant
    url:      Restaurant url
    """
    # driver = webdriver.Chrome()

    driver = webdriver.Chrome(options=options )
    basic_url = (url+'?start={}')  # 替换为实际的评论页面URL
    
    res = driver.get(url)
    # driver.implicitly_wait(2) # gives an implicit wait for 20 seconds

    time.sleep(2)
    # driver.maximize_window() # For maximizing window

    parser = BeautifulSoup(driver.page_source, 'html.parser')
    check_unclaimed = driver.find_elements(By.XPATH,'//span[contains(@class," css-1luukq")]/span[contains(@class," hovercard-trigger__09f24__qn3fP")]/div[contains(@class," css-v3nuob")]/span[contains(@class,"bullet--")]/a[contains(@class,"css-19v1rkv")]')

    try:
        element = driver.find_element(By.XPATH,'//section[contains(@class," css-ufd2i")]/div[contains(@class," css-1qn0b6x")]/div[contains(@class,"pagination__09f24__VRjN4 css-5hgtfb")]/div[contains(@class,"css-1aq64zd")]/span[contains(@class,"css-chan6m")]')
    except NoSuchElementException:
        return []        
    # element = driver.find_element(By.CSS_SELECTOR,'div.css-1aq64zd span.css-chan6m')
    all_reviews = []
    total_page_num = get_max_page(element)

    for page in range(0, total_page_num*10, 10):
        
        if page != 0:
            url = basic_url.format(page)
        driver.get(url)
        # 等待页面加载完成，你可以根据实际情况增加等待时间
        wait = WebDriverWait(driver, 10)
        date_elements = driver.find_elements(By.XPATH,'//li[contains(@class," css-1q2nwpv")]/div[contains(@class," css-1qn0b6x")]/div[contains(@class," css-10n911v")]/div[contains(@class,"arrange__09f24__LDfbs gutter-1__09f24__yAbCL vertical-align-middle__09f24__zU9sE css-1qn0b6x")]/div[contains(@class, "arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG css-1qn0b6x")]/span[contains(@class, " css-chan6m")]')

  
        place_elements = driver.find_elements(By.XPATH, '//div[contains(@class," css-1qn0b6x")]/span[contains(@class," css-qgunke")]')

        user_links = parser.find_all('a', attrs={"class": "css-19v1rkv", "role": "link", "href": lambda href: href and href.startswith("/user_details?userid=")})
        
        rating_elements = driver.find_elements(By.XPATH, '//div[contains(@class," css-10n911v")]/div[contains(@class,"arrange__09f24__LDfbs gutter-1__09f24__yAbCL vertical-align-middle__09f24__zU9sE css-1qn0b6x")]/div[contains(@class,"arrange-unit__09f24__rqHTg css-1qn0b6x")]/span[contains(@class," css-1d8srnw")]/div[contains(@class,"five-stars__09f24__mBKym five-stars--regular__09f24__DgBNj css-1jq1ouh") or contains(@class,"css-14g69b3")]')


        review_elements = parser.find_all('p', attrs={"class": "comment__09f24__D0cxf css-qgunke"})
        icon_elements = driver.find_elements(By.XPATH,'//span[contains(@class,"css-inq9gi")]/div[contains(@class,"arrange__09f24__LDfbs gutter-0-5__09f24__PjGWv vertical-align-middle__09f24__zU9sE css-1qn0b6x")]/div[contains(@class,"arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG css-1qn0b6x")]')
        useful_list = []
        funny_list = []
        cool_list = []
        cnt = 0
        for span in icon_elements:
            words = span.text.split(' ')
            if len(words) > 1:
                value = words[1]
            else:
                value = 0
            if cnt%3==0:
                useful_list.append(value)
            elif cnt%3==1:
                funny_list.append(value)
            elif cnt%3==2:
                cool_list.append(value)
            cnt = cnt + 1
        for i in range(len(date_elements)):
            review_info = {
                "Date": date_elements[i].text,
                "Place": place_elements[0:][i].text,
                "User": user_links[i].text,
                "Rating": rating_elements[i].get_attribute("aria-label"),
                "useful":useful_list[i],
                "funny":funny_list[i],
                "cool":cool_list[i],
                "Review": review_elements[i].text,

            }
            all_reviews.append(review_info)            
    driver.quit()
    
    return all_reviews


url_list = [
            'https://www.yelp.com/biz/soup-dumpling-plus-fort-lee',
            'https://www.yelp.com/biz/gopchang-story-fort-lee-fort-lee',
            'https://www.yelp.com/biz/soba-noodle-azuma-fort-lee-2',
            'https://www.yelp.com/biz/sa-rit-gol-fort-lee-2',
            'https://www.yelp.com/biz/lauren-s-chicken-burger-fort-lee',
            'https://www.yelp.com/biz/gamja-tang-tang-fort-lee',
            'https://www.yelp.com/biz/oiso-bbq-pit-fort-lee-2',
            'https://www.yelp.com/biz/capt-loui-fort-lee-2',
            'https://www.yelp.com/biz/martys-fort-lee',
            'https://www.yelp.com/biz/sushi-kai-fort-lee',
            'https://www.yelp.com/biz/wok-bar-fort-lee']

if __name__ == "__main__":
    total_info = []
    for i in range(len(url_list)):
        info = scrap_review(url_list[i])
        info = organize_info(info)
        total_info.append(info)
        print("The", i+1, "business scraping success!")

    total_info = organize_info(total_info)
    import pandas as pd
    print(len(total_info))

    mini_data = pd.DataFrame(total_info)
    mini_data.to_csv('mini_review_dataset.csv', encoding='utf-8')
    mini_data.head()
