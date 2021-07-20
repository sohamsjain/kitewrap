from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
from urllib.parse import urlparse
from os.path import join, dirname

chromedriver_path = join(dirname(__file__), r'chromedriver.exe')


def get_request_token(url, user_id, password, pin, headless=True):
    chrome_options = Options()
    chrome_options.headless = headless
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
    driver.get(url)
    sleep(1)
    userid = driver.find_element_by_xpath('//*[@id="userid"]')
    userid.clear()
    userid.send_keys(user_id)
    password_box = driver.find_element_by_xpath('//*[@id="password"]')
    password_box.clear()
    password_box.send_keys(password)
    login = driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[4]/button')
    login.click()
    sleep(1)
    pin_box = driver.find_element_by_xpath('//*[@id="pin"]')
    pin_box.clear()
    pin_box.send_keys(pin)
    continue_button = driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[3]/button')
    continue_button.click()
    url = str(driver.current_url)
    parsed_url = urlparse(url)
    if parsed_url.netloc != '127.0.0.1:3000':
        sleep(1)
        url = str(driver.current_url)
        parsed_url = urlparse(url)
    query = parsed_url.query
    query_list = query.split("&")
    query_dict = {}
    for q in query_list:
        ql = q.split("=")
        k, v = ql[0], ql[1]
        query_dict.update({k: v})
    request_token = query_dict['request_token']
    driver.close()
    return request_token