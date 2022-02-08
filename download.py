import logging
import sys
from configparser import ConfigParser

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By


def download(tag, tab):
    logging.info('Searching your tag...')
    tab.get('https://exhentai.org/?f_search=' + tag)
    pages = tab.find_elements(by=By.XPATH, value='//table[@class="ptb"]/tbody/tr/td')
    last_page = pages[len(pages) - 1].find_element(by=By.XPATH, value='//table[@class="ptb"]/tbody/tr/td[' + str(
        len(pages) - 1) + ']/a')
    logging.info(last_page.text + ' pages in total.')
    current_page = int(last_page.text) - 1
    for i in range(current_page, -1, -1):
        logging.info('Switching page to ' + str(i + 1) + '...')
        if current_page == 0:
            tab.get('https://exhentai.org/?f_search=' + tag)
        else:
            tab.get('https://exhentai.org/?page=' + str(i) + '&f_search=' + tag)
        trs = tab.find_elements(by=By.XPATH, value='//table[@class="itg gltc"]/tbody/tr')
        jump_title = True
        for tr in trs:
            if jump_title:
                jump_title = False
                continue
            link = tr.find_element(by=By.XPATH, value='td[@class="gl3c glname"]/a').get_attribute('href')
            name = tr.find_element(by=By.XPATH, value='td[@class="gl3c glname"]/a/div[@class="glink"]').text
            logging.info('Downloading ' + name + '...')
            download_single(link)


def download_single(link):
    print(link)


config = ConfigParser()
config.read('config.cfg')
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
logging.info('Checking Chrome Driver...')
driverLocation = "chromedriver"
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-gpu')
# options.add_argument("--window-size=1920,3840")

try:
    browser = webdriver.Chrome(executable_path=driverLocation, options=options)
except WebDriverException as e:
    logging.error('Chrome Driver not found. Please download it from https://chromedriver.chromium.org/downloads')
    input('Press Enter to exit...')
    sys.exit(1)
logging.info('Loading... Make sure you have a stable internet connection.')
browser.get('https://exhentai.org/')
browser.add_cookie({'name': 'ipb_member_id', 'value': config.get('cookies', 'ipb_member_id')})
browser.add_cookie({'name': 'ipb_pass_hash', 'value': config.get('cookies', 'ipb_pass_hash')})
browser.add_cookie({'name': 'igneous', 'value': config.get('cookies', 'igneous')})
browser.get('https://exhentai.org/')
tags = input('Please input tags, use + to split every tag.\n')
download(tags, browser)
input('Finished.\nPress Enter to exit...')
browser.quit()
