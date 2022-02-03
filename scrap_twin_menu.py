# -*- coding: utf-8 -*-

import os
import time
import datetime

import fire

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import pandas as pd

MY_ID = os.environ["MY_ID"]
MY_PW = os.environ["MY_PW"]

CHROME_DRIVER_PATH = os.environ["CHROME_DRIVER_PATH"]

def set_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def login(driver):
    to_login_btn =  WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,\
        "#menu > table > tbody > tr:nth-child(1) > td.sc > div > ul > li > a:nth-child(1)")))
    to_login_btn.click()
    time.sleep(2)

    id_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#id")))
    password_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#password")))

    id_box.clear()
    id_box.send_keys(MY_ID)
    time.sleep(0.5)

    password_box.clear()
    password_box.send_keys(MY_PW)
    time.sleep(0.5)

    login_btn =  WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,\
        "#contents > div > div > fieldset > p.bt_login > a > img")))
    login_btn.click()
    time.sleep(2)

def go_east(driver):
    go_east_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,\
    "#mealCafeCd > option:nth-child(2)")))
    go_east_btn.click()

def get_meal_info(soup, css_selector):
    menu_table = soup.select_one(css_selector)
    menu_detail = menu_table.find_all("tr")

    weekday = [w.text for w in menu_detail[0].find_all("th")[1:]]
    #1, 3, 5
    category = menu_detail[5]
    menu_df = pd.DataFrame()
    for category in menu_detail[1::2]:

        tmp = category.findAll("td")

        course_title = tmp[0].text

        menu_list = []

        for i in range(1,4):
            menu_list.append([m.text for m in tmp[i].findAll("li")])

        menu_df = pd.concat([menu_df, pd.DataFrame({course_title:menu_list}, index=weekday).transpose()])

    return menu_df

def show_current_screen(driver):
    driver.save_screenshot("tmp.png")
    pil_im = Image.open("tmp.png")
    display(pil_im)
    os.remove("tmp.png")

def main(building):
    today = datetime.datetime.now()
    is_monday = today.weekday() == 0

    if True:

        driver = set_driver()

        try:

            base_url = "https://lgtwintowers.co.kr/"
            main_url = "common/index_cs.dev"

            driver.get(base_url + main_url)
            time.sleep(3)

            login(driver)

            menu_url = "/board/food/ourhomeBoard/ourhomeBdWeek.dev"
            driver.get(base_url + menu_url)
            time.sleep(3)
            
            if building == "west":
                pass
            elif building == "east":
                go_east(driver)
                pass

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            menu_df = pd.concat([get_meal_info(soup, "#mealLeft > table > tbody"),
                    get_meal_info(soup, "#mealRight > table > tbody").iloc[:,1:]], axis=1)

            tmp = menu_df.columns.str.replace("\)|\/","")
            tmp = tmp.str.split("(")

            current_year = datetime.datetime.now().year
            menu_df.columns = [t[0] + "_" + str(current_year) + t[1] for t in tmp]

            monday = today - datetime.timedelta(days=today.weekday())

            if not os.path.exists("./storage"):
                os.makedirs("./storage")
                
            menu_df.to_csv(f"./storage/twin_menu_{building}_{monday.strftime('%Y%m%d')}.csv", encoding="UTF-8")
        
        except Exception as e:
            raise e

        finally:
            driver.quit()

if __name__ == "__main__":
    fire.Fire()