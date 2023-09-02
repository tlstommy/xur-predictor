#scapre historical data from wherexur that was indexed before xurtracker with selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
import time


SEASON_MAX = 21
season = 1

driver = webdriver.Chrome()

while season <= SEASON_MAX:
    URL = f"https://wherexur.com/{season}"
    driver.get(URL)
    
    #wait for data to download
    driver.implicitly_wait(120)
    lists = driver.find_elements(By.CLASS_NAME, "list")
    print(lists)
    links = driver.find_elements(By.CSS_SELECTOR, "li.linked a")
    #print(links)
    for link in links:
        print(link.get_attribute('href'))
    
    season += 1

driver.quit()
