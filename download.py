import logging
import os
import sys
import urllib.request
from configparser import ConfigParser
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By


def download(tag, tab, is_continue=False, page_number=0, config_tag=None):
    if not is_continue:
        os.makedirs(tag, exist_ok=True)
        os.chdir(tag)
        config_tag = ConfigParser()
        config_tag.add_section('progress')
        config_tag.write(open(tag + '.ini', 'w'))
        logging.info('Searching your tag...')
        tab.get('https://exhentai.org/?f_search=' + tag)
        pages = tab.find_elements(by=By.XPATH, value='//table[@class="ptb"]/tbody/tr/td')
        last_page = pages[len(pages) - 1].find_element(by=By.XPATH, value='//table[@class="ptb"]/tbody/tr/td[' + str(
            len(pages) - 1) + ']/a')
        if last_page is None:
            logging.info('No result found!')
            return
        logging.info(last_page.text + ' pages in total.')
        current_page = int(last_page.text) - 1
    else:
        current_page = page_number
    for i in range(current_page, -1, -1):
        config_tag.set('progress', 'current_page', str(current_page))
        config_tag.write(open(tag + '.ini', 'w'))
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
            os.makedirs(name, exist_ok=True)
            os.chdir(name)
            download_single(link, tab)
            os.chdir('..')
            config_tag.set('progress', 'current_name', name)
            config_tag.write(open(tag + '.ini', 'w'))


def download_single(link, tab):
    tab.execute_script('window.open("about:blank")')
    tab.switch_to.window(tab.window_handles[1])
    tab.get(link)
    pages = tab.find_elements(by=By.XPATH, value='//table[@class="ptb"]/tbody/tr/td')
    last_page = pages[len(pages) - 1].find_element(by=By.XPATH, value='//table[@class="ptb"]/tbody/tr/td[' + str(
        len(pages) - 1) + ']/a')
    logging.info(last_page.text + ' pages in total.')
    current_page = int(last_page.text) - 1
    for i in range(current_page, -1, -1):
        logging.info('Switching page to ' + str(i + 1) + '...')
        if current_page == 0:
            tab.get(link)
        else:
            tab.get(link + '?p=' + str(i))
        images = tab.find_elements(by=By.XPATH, value='//div[@class="gdtm"]/div/a')
        for image in images:
            download_image(image.get_attribute('href'), tab)
    tab.close()
    tab.switch_to.window(tab.window_handles[0])


def download_image(link, tab):
    logging.info('Downloading image ' + link + '...')
    tab.execute_script('window.open("about:blank")')
    tab.switch_to.window(tab.window_handles[2])
    tab.get(link)
    image_link = tab.find_element(by=By.XPATH, value='//div[@id="i3"]/a/img').get_attribute('src')
    print(image_link)
    urllib.request.urlretrieve(image_link, image_link.rpartition('/')[2])
    tab.close()
    tab.switch_to.window(tab.window_handles[1])


def check_tags(tag, tab):
    os.chdir(tag)
    if not os.path.exists(tag + '.ini'):
        logging.info('Unable to find a progress file!\nPlease delete the tag name folder and try again!')
    logging.info('Download history found: ' + tag)
    config_tag = ConfigParser()
    config_tag.read(tag + '.ini')
    tab.get('https://exhentai.org/?f_search=' + tag)
    pages = tab.find_elements(by=By.XPATH, value='//table[@class="ptb"]/tbody/tr/td')
    last_page = pages[len(pages) - 1].find_element(by=By.XPATH, value='//table[@class="ptb"]/tbody/tr/td[' + str(
        len(pages) - 1) + ']/a')
    if last_page is None:
        logging.info('No result found!')
        return
    logging.info(last_page.text + ' pages in total.')
    is_found = False
    found_page = 0
    for current_page in range(int(config_tag.get('progress', 'current_page')), last_page):
        tab.get('https://exhentai.org/?page=' + str(current_page) + '&f_search=' + tag)
        trs = tab.find_elements(by=By.XPATH, value='//table[@class="itg gltc"]/tbody/tr')
        for tr in trs:
            if tag != tr.find_element(by=By.XPATH, value='td[@class="gl3c glname"]/a/div[@class="glink"]').text:
                continue
            else:
                is_found = True
                found_page = current_page
                logging.info('Found the last downloaded location at page ' + str(current_page))
                break
    if not is_found:
        logging.info('Cannot find the position of last download!')
    else:
        download(tag, tab, True, found_page, config_tag)


config = ConfigParser()
config.read('config.cfg')
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
logging.info('Checking Chrome Driver...')
driverLocation = "chromedriver"
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument("--window-size=1920,3840")

try:
    browser = webdriver.Chrome(executable_path=driverLocation, options=options)
except WebDriverException:
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
if Path(tags).exists():
    check_tags(tags, browser)
else:
    download(tags, browser)
input('Script finished.\nPress Enter to exit...')
browser.quit()
