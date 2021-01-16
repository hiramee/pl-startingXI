from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import boto3

base_xpath = '//*[@id="mainContent"]/div/section[2]/div[2]/div[2]/div[2]/section[2]/div/div/'
xpath_arr_home = []
xpath_arr_away = []


def lambda_handler(event, context):
    id = event['id']
    my_url = f'https://www.premierleague.com/match/{id}'
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = '/opt/webdriverlayer/headless-chromium'
    driver = webdriver.Chrome(
        '/opt/webdriverlayer/chromedriver',
        options=options
    )
    driver.get(my_url)
    home_team = driver.find_element_by_xpath(
        '//*[@id="mainContent"]/div/section/div[2]/section/div[3]/div/div/div[1]/div[1]/a[2]/span[1]').text
    away_team = driver.find_element_by_xpath(
        '//*[@id="mainContent"]/div/section/div[2]/section/div[3]/div/div/div[1]/div[3]/a[2]/span[1]').text
    print(home_team)
    print(away_team)

    cookie_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/section/div/div')))
    cookie_btn.click()

    elem = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="mainContent"]/div/section[2]/div[2]/div[2]/div[1]/div/div/ul/li[2]')))
    elem.click()

    for i in range(1, 5):
        if i == 1:
            addXpathArr(xpath_arr_home, 1, i, 1)
            addXpathArr(xpath_arr_away, 3, i, 1)
        elif i == 4:
            for j in range(1, 4):
                addXpathArr(xpath_arr_home, 1, i, j)
                addXpathArr(xpath_arr_away, 3, i, j)
        else:
            for j in range(1, 6):
                addXpathArr(xpath_arr_home, 1, i, j)
                addXpathArr(xpath_arr_away, 3, i, j)

    player_arr_home = []
    player_arr_away = []
    for item in xpath_arr_home:
        try:
            player = driver.find_element_by_xpath(item).text
            player_arr_home.append(player)
        except NoSuchElementException:
            continue
    for item in xpath_arr_away:
        try:
            player = driver.find_element_by_xpath(item).text
            player_arr_away.append(player)
        except NoSuchElementException:
            continue
    dic = dict(home=player_arr_home, away=player_arr_away)
    print(dic)
    driver.quit()

    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    account_id = identity['Account']

    client = boto3.client('sns')
    response = client.publish(
        TargetArn='arn:aws:sns:ap-northeast-1:' + account_id + ':PublishPLStartingXI',
        Subject=home_team+away_team,
        Message=json.dumps(dic)
    )


def addXpathArr(arr, home, position, number):
    xpath = base_xpath + 'div[' + str(home) + ']/div/div/ul[' + str(
        position) + ']/li[' + str(number) + ']/a/div[2]/span[1]'
    arr.append(xpath)
