import pymysql
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import re
import pandas as pd
from pandas import DataFrame
from IPython.display import display
import sqlalchemy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from time import sleep
import json

from workers.databaser import MySQL

from bs4 import BeautifulSoup


class DataUpdate():
    def __init__(self):
        self.updateData()

    def updateData(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        driver = webdriver.Chrome(options=options)
        driver.get("https://dealer.heydealer.com/")
        driver.implicitly_wait(3)

        driver.find_element_by_name("username").send_keys("dyf0505")
        driver.find_element_by_name("password").send_keys("qaz100")
        driver.find_element_by_xpath('//button[@class="_eaaa748"]').click()

        sleep(1)

        sql = "SELECT * FROM {} ".format(
            'heydealer_car_data')

        self.my_db = pymysql.connect(host='grdver.xyz',
                                     port=3306,
                                     user='healer',
                                     password='7974',
                                     db='HeyHealer',
                                     charset='utf8',
                                     autocommit=True,
                                     cursorclass=pymysql.cursors.DictCursor)

        with self.my_db:
            with self.my_db.cursor() as cur:
                cur.execute(sql)
                car_list = cur.fetchall()

        
        
        for value in car_list:

            try: 
                option_load = json.loads(value['json_options'])
                print(option_load['옵션'])

                url = value['url']
                driver.get(url)

                # 차량 전체 페이지 html 파싱.
                try:
                    page = WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                        (By.XPATH, '''//div[@class="_87edb25"]'''))).get_attribute('innerHTML')
                    self.soup = BeautifulSoup(page, 'html.parser')
                except:
                    MySQL().deleteWhereColumn('heydealer_car_data', 'url', url)
                    continue

                """ 옵션 입력 """

                display_option = self.soup.select_one('div._1192e02') if self.soup.select_one(
                    'div._1192e02') != None else self.soup.select_one('div._cf3bda0')
                option_texts = display_option.find_all(
                    'div', {'class': ['_dd8265f undefined', '_dd8265f _d7384d3', '_a3c75ff _655a132']})

                all_option = display_option.find_all('div', {'class': [
                    '_dd8265f undefined', '_dd8265f _d7384d3', '_dd8265f _df838f5', '_a3c75ff _655a132', '_a3c75ff']})
                self.all_options = []
                if all_option != None:
                    for index, value in enumerate(all_option):
                        if value.get_text() == "" or value.text == "\n":
                            continue

                        self.all_options.append(
                            value.text.replace('?', '').strip('\n'))

                self.text_options = ""
                self.options = []
                if option_texts != None:
                    for index, value in enumerate(option_texts):
                        if value.get_text() == "" or value.text == "\n":
                            continue

                        self.text_options = self.text_options + \
                                            value.text.replace('?', '').strip('\n') + '\n'

                        self.options.append(
                            value.text.replace('?', '').strip('\n'))

                add_option_texts = display_option.find_all(
                    'div', {'class': ['_dd8265f _d7384d3']})

                self.text_add_options = ""
                self.add_options = []
                if add_option_texts != None:
                    for index, value in enumerate(add_option_texts):
                        if value.text == "" or value.text == "\n":
                            continue

                        self.text_add_options = self.text_add_options + \
                                                value.text.replace('?', '').strip('\n') + '\n'

                        self.add_options.append(
                            value.text.replace('?', '').strip('\n'))

                self.opt_list = {"옵션": self.options,
                                "추가옵션": self.add_options, "전체옵션": self.all_options}
                self.json_options = json.dumps(self.opt_list, ensure_ascii=False)
                self.json_options = json.dumps(self.json_options, ensure_ascii=False)

                """ 옵션 입력 완료 """

                self.my_db = pymysql.connect(host='grdver.xyz',
                                            port=3306,
                                            user='healer',
                                            password='7974',
                                            db='HeyHealer',
                                            charset='utf8',
                                            autocommit=True,
                                            cursorclass=pymysql.cursors.DictCursor)

                sql = "UPDATE heydealer_car_data SET json_options = %s WHERE url = '{}'".format(
                    url)
                with self.my_db:
                    with self.my_db.cursor() as cur:
                        cur.execute(sql, (self.json_options))
                        self.my_db.commit

                print(self.json_options)
            except:
                pass


if __name__ == '__main__':
    app = DataUpdate()
    
    
