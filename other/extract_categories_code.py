from time import sleep
import numpy as np
from selenium import webdriver
import pandas as pd
from IPython.display import display
import pymysql
from sqlalchemy import create_engine

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

heydealer_url = "https://dealer.heydealer.com/"


class Extractor():

    def __init__(self, url):
        self.url = url
        self.sleep_time = 0.05

    def extract(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        driver.implicitly_wait(3)

        driver.find_element_by_name("username").send_keys("dyf0505")
        driver.find_element_by_name("password").send_keys("qaz100")
        driver.find_element_by_xpath('//button[@class="_eaaa748"]').click()

        sleep(1)

        self.cate_page_url = "https://dealer.heydealer.com/chart?period=c"

        driver.get(self.cate_page_url)

        # _36646a4
        brands_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
            (By.XPATH, '''//div[@class="_36646a4" or @class="_36646a4 _67941ef"]''')))

        for i_brand, brand_element in enumerate(brands_elements, start=1):

            if i_brand < 8:
                continue

            xpath = '//div[@class="_36646a4" or @class="_36646a4 _67941ef"][' + \
                str(i_brand) + ']'
            brand_click_element = driver.find_element_by_xpath(
                xpath + '//canvas')
            driver.execute_script("arguments[0].click();", brand_click_element)
            sleep(self.sleep_time)

            # _76e846c
            try:
                model_group_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                    (By.XPATH, '''//div[@class="_76e846c"]//div[@class="_36646a4" or @class="_36646a4 _67941ef"]''')))
            except:
                brand_click_element = driver.find_element_by_xpath(
                    '//div[@class="_22e3f17"]//canvas')
                driver.execute_script(
                    "arguments[0].click();", brand_click_element)
                sleep(self.sleep_time)

                continue

            for i_model_group, model_group_element in enumerate(model_group_elements, start=1):

                xpath = '//div[@class="_76e846c"]//div[@class="_36646a4" or @class="_36646a4 _67941ef"][' + str(
                    i_model_group) + ']'
                model_group_click_element = driver.find_element_by_xpath(
                    xpath + '//canvas')
                driver.execute_script(
                    "arguments[0].click();", model_group_click_element)

                # _4bb7cb5
                try:
                    model_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                        (By.XPATH, '''//div[@class="_4bb7cb5"]//div[@class="_36646a4" or @class="_36646a4 _67941ef"]''')))
                except:
                    model_group_click_element = driver.find_element_by_xpath(
                        '//div[@class="_b6a189c"]//canvas')
                    driver.execute_script(
                        "arguments[0].click();", model_group_click_element)
                    sleep(self.sleep_time)

                    continue

                for i_model, model_element in enumerate(model_elements, start=1):

                    xpath = '//div[@class="_4bb7cb5"]//div[@class="_36646a4" or @class="_36646a4 _67941ef"][' + str(
                            i_model) + ']'
                    model_click_element = driver.find_element_by_xpath(
                        xpath + '//canvas')
                    driver.execute_script(
                        "arguments[0].click();", model_click_element)
                    sleep(self.sleep_time)

                    # _f29b812
                    try:
                        grade_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                            (By.XPATH, '''//div[@class="_f29b812"]//div[@class="_36646a4" or @class="_36646a4 _67941ef"]''')))
                    except:
                        model_click_element = driver.find_element_by_xpath(
                            '//div[@class="_47602a3"]//canvas')
                        driver.execute_script(
                            "arguments[0].click();", model_click_element)
                        sleep(self.sleep_time)

                        continue

                    for i_grade, grade_element in enumerate(grade_elements, start=1):

                        """ 등급 """

                        grade_xpath = '//div[@class="_f29b812"]//div[@class="_36646a4" or @class="_36646a4 _67941ef"][' + str(
                            i_grade) + ']'
                        grade_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                            (By.XPATH, grade_xpath + '//a[@class="_53bc07b"]'))).text

                        if grade_name == "전체등급":
                            continue

                        grade_click_element = driver.find_element_by_xpath(
                            grade_xpath + '//canvas')
                        driver.execute_script(
                            "arguments[0].click();", grade_click_element)
                        sleep(self.sleep_time)

                        get_url = driver.current_url

                        grade_find_index = get_url.find("grades=")

                        for text_i, char in enumerate(get_url):
                            if char == "&":
                                if text_i > grade_find_index:
                                    grade_find_next_and_index = text_i
                                    break

                        grade_get_code = get_url[grade_find_index:grade_find_next_and_index]

                        """ 제조사 """
                        brand_xpath = '//div[@class="_22e3f17"]'

                        brand_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                            (By.XPATH, brand_xpath + '//a[@class="_53bc07b"]'))).text

                        brand_find_index = get_url.find("brand=")

                        for text_i, char in enumerate(get_url):
                            if char == "&":
                                if text_i > brand_find_index:
                                    brand_find_next_and_index = text_i
                                    break

                        brand_get_code = get_url[brand_find_index:brand_find_next_and_index]

                        """ 모델 """
                        xpath = '//div[@class="_b6a189c"]'
                        model_group_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                            (By.XPATH, xpath + '//a[@class="_53bc07b"]'))).text

                        sleep(self.sleep_time)
                        model_group_find_index = get_url.find(
                            "model_group=")

                        for text_i, char in enumerate(get_url):
                            if char == "&":
                                if text_i > model_group_find_index:
                                    model_group_find_next_and_index = text_i
                                    break

                        model_group_get_code = get_url[
                            model_group_find_index:model_group_find_next_and_index]

                        """ 모델 상세 """
                        xpath = '//div[@class="_47602a3"]'
                        model_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                            (By.XPATH, xpath + '//a[@class="_53bc07b"]'))).text

                        model_find_index = get_url.find("model=")

                        for text_i, char in enumerate(get_url):
                            if char == "&":
                                if text_i > model_find_index:
                                    model_find_next_and_index = text_i
                                    break

                        model_get_code = get_url[model_find_index:model_find_next_and_index]

                        data = {
                            'brand': [brand_name],
                            'model_group': [model_group_name],
                            'model': [model_name],
                            'grade': [grade_name],
                            'brand_code': [brand_get_code],
                            'model_group_code': [model_group_get_code],
                            'model_code': [model_get_code],
                            'grade_code': [grade_get_code],
                        }

                        print(brand_name + " : " + brand_get_code + " , " + model_group_name + " : " + model_group_get_code +
                              " , " + model_name + " : " + model_get_code + " , " + grade_name + " : " + grade_get_code)

                        # 동일한 카테고리 확인.
                        my_db = pymysql.connect(host='grdver.xyz',
                                                port=3306,
                                                user='healer',
                                                password='7974',
                                                db='HeyHealer',
                                                charset='utf8',
                                                autocommit=True,
                                                cursorclass=pymysql.cursors.DictCursor)

                        sql = "SELECT * FROM categories WHERE brand = '{}' and model_group = '{}' and model = '{}' and grade = '{}'".format(
                            brand_name, model_group_name, model_name, grade_name)

                        with my_db:
                            with my_db.cursor() as cur:
                                cur.execute(sql)
                                if len(cur.fetchall()) == 0:
                                    self.saveDatabase(data)

                        xpath = '//div[@class="_f29b812"]//div[@class="_36646a4" or @class="_36646a4 _67941ef"][' + str(
                            i_grade) + ']'
                        grade_click_element = driver.find_element_by_xpath(
                            xpath + '//canvas')
                        driver.execute_script(
                            "arguments[0].click();", grade_click_element)
                        sleep(self.sleep_time)

                    model_click_element = driver.find_element_by_xpath(
                        '//div[@class="_47602a3"]//canvas')
                    driver.execute_script(
                        "arguments[0].click();", model_click_element)
                    sleep(self.sleep_time)

                model_group_click_element = driver.find_element_by_xpath(
                    '//div[@class="_b6a189c"]//canvas')
                driver.execute_script(
                    "arguments[0].click();", model_group_click_element)
                sleep(self.sleep_time)

            brand_click_element = driver.find_element_by_xpath(
                '//div[@class="_22e3f17"]//canvas')
            driver.execute_script("arguments[0].click();", brand_click_element)
            sleep(self.sleep_time)

    def saveDatabase(self, data):
        engine = create_engine("mysql+pymysql://healer:" + "7974" +
                               "@grdver.xyz/HeyHealer", encoding='utf-8')
        conn = engine.connect()

        df_mysql_data = pd.DataFrame(data)
        df_mysql_data.to_sql(name='categories', con=engine,
                             if_exists='append', index=False)

        conn.close()


if __name__ == '__main__':
    app = Extractor(heydealer_url)
    app.extract()
