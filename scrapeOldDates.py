#scapre historical data from wherexur that was indexed before xurtracker with selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

urlList = []

SEASON_MAX = 21
season = 1

driver = webdriver.Chrome()
#wait for data to download
driver.implicitly_wait(120)


def getLocation(url):
    driver.get(url)

    location = driver.find_element(By.CLASS_NAME, "destination")
    return location.text

while season <= SEASON_MAX:

    URL = f"https://wherexur.com/{season}"
    driver.get(URL)
    
    

    links = driver.find_elements(By.CSS_SELECTOR, "li.linked a")
    #print(links)

    for link in links:
        link = link.get_attribute('href').replace("https://wherexur.com/","")
        if "item" in link:
            continue
        if "/" in link:
            print(f"https://wherexur.com/{link}")
            urlList.append(f"https://wherexur.com/{link}")


    season += 1

print(urlList)
print(urlList.sort())
driver.quit()
