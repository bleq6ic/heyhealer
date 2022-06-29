from logging import warning
from math import ceil, floor
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json

import re

from IPython.display import display

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from sqlalchemy import null

from workers.databaser import MySQL

import pymysql.cursors
import pymysql

import pandas as pd

from bs4 import BeautifulSoup

from time import sleep

from datetime import datetime

from workers.calculator import EstimateCalculators


class EstimateCalculator(QThread):

    estimate_price_signal = pyqtSignal(int)
    # 임시로 메모 시그널 연결. 추후에 힐러db 데이터 예측 및 엔카 데이터 예측 등..
    next_calculator_signal = pyqtSignal(str)

    def __init__(self, parent, heyhealer_parent, car_gui_parent):
        super().__init__()
        self.parent = parent
        self.heyhealer_parent = heyhealer_parent
        self.car_gui_parent = car_gui_parent
        self.original_url = self.heyhealer_parent.car_url
        self.driver = self.heyhealer_parent.driver
        self.car_data = self.heyhealer_parent.curr_car_data

        if self.car_gui_parent != None:
            self.estimate_price_signal.connect(
                self.car_gui_parent.setEstimatePrice)

        # 임시로 메모 시그널 연결. 추후에 힐러db 데이터 예측 및 엔카 데이터 예측 등..
        self.next_calculator_signal.connect(
            self.heyhealer_parent.inputEstimatePrice)

        self.run_calculator = True

    def run(self):

        while self.run_calculator:

            # 엔카

            data_list = self.extractHeydealerDB()  # dataframe 타입으로 반환.
            healer_db_list = self.extractHealerDB()
            encar_low = self.extractEncar()

            min_damage_price = 500

            # 예상가 산출.
            """
            estimate_price_test1 = EstimateCalculators().hdCalculatorVer2(
                self.car_data, data_list.copy()) - self.deductor(self.car_data)
            estimate_price_test2 = EstimateCalculators().hhCalculatorVer1(
                self.car_data, healer_db_list.copy()) - self.deductor(self.car_data)
            

            if estimate_price_test1 <= 0:
                estimate_price = 0
            else:
                estimate_price = estimate_price_test1
            """

            # 헤이딜러 자료 텍스트화.
            if len(data_list) > 0:
                low_data = data_list[0]
                heydealer_low_price_text = "1) " + str(low_data['max_price']) + " 만원 (헤이딜러 매입시세)\n" + str(low_data['grade']) + "\n" + str(low_data['bidder']) + " 명 입찰 (" + str(len(data_list)) + " 개의 데이터 중 최저가)\n" + str(low_data['years']) + "/" + str(low_data['month']) + " (" + str(low_data['car_years']) + "), " + str(low_data['mileage']) + " km, " + str(low_data['color']) + "\n" + str(low_data['accident']) + "\n\n"
            else:
                heydealer_low_price_text = "1) 검색된 매물 0 개 (헤이딜러 매입시세)\n\n"

            # 데이터베이스 자료 텍스트화.
            if len(healer_db_list) > 0:
                db_low_data = healer_db_list[0]

                """ 사고 유무 (교환, 판금, 도색 갯수) """
                json_acc_repairs = json.loads(db_low_data['json_accident_repairs'])
                changed_count_text = "교환 : " + str(len(json_acc_repairs['교환'])) + " 개, "
                sheeting_count_text = "판금 : " + str(len(json_acc_repairs['판금'])) + " 개, "
                paint_count_text = "도색 : " + str(len(json_acc_repairs['도색'])) + " 개"

                new_price_text = str(db_low_data['car_new_price']) + " 만원" if db_low_data['car_new_price'] > 0 else "신차가격정보 없음"

                """ 내차피해액 """
                damaged_count_text = "내차피해액 : 없음"
                damaged_count = 0
                try:
                    if db_low_data['json_my_car_damaged'] != None:
                        json_my_car_damaged = json.loads(db_low_data['json_my_car_damaged'])
                        for i, v in enumerate(json_my_car_damaged['수리비']):
                            damaged_count = damaged_count + int(v)
                        
                        damaged_count_text = "내차피해액 : " + str(damaged_count) + " 만원\n"
                except:
                    pass
                
                heyhealer_low_price_text = "2) " + str(db_low_data['max_price']) + " 만원 (데이터베이스)\n" + str(low_data['grade']) + "\n" + "출고가(옵션포함) : " + new_price_text + "\n" + str(low_data['years']) + "/" + str(db_low_data['month']) + " (" + str(db_low_data['car_years']) + "), " + str(db_low_data['mileage']) + " km, " + str(db_low_data['color']) + "\n" + str(db_low_data['accident']) + "\n(" + changed_count_text + sheeting_count_text + paint_count_text +")\n"+ damaged_count_text + "\n\n"
            else:
                heyhealer_low_price_text = "2) 검색된 매물 0 개 (데이터베이스)\n\n"

            encar_price_text = "3) " + str(encar_low['price']) + " 만원 (엔카 최저가)\n" + str(encar_low['car_detail']) + "\n" + str(
                encar_low['car_years']) + " , " + str(encar_low['mileage']) + " km, " + str(encar_low['color']) + "\n" + "교환: " + str(
                    encar_low['changed']) + ", 판금: " + str(encar_low['sheeting']) + ", 부식: " + str(encar_low['corrosion']) + "\n내차피해액 : " + str(encar_low['my_car_damaged']) + " 원\n" + str(encar_low['add_options']) + "\n\n" if encar_low != None else "3) 비교 대상 부족 (엔카 최저가)\n"

            alert_text = "경고) 내차피해 총액 {} 만원 초과 \n\n".format(
                min_damage_price) if self.car_data['total_my_car_damage'] > min_damage_price else ""

            warning_text = "** " + str(self.deductor(self.car_data)) + " 만원을 감가하고 입찰해주세요 **\n\n"

            e_text = alert_text + \
                warning_text + \
                heydealer_low_price_text + \
                heyhealer_low_price_text + \
                encar_price_text
                

            # url 차량 정보 윈도우에 예상가 표시.
            self.estimate_price_signal.emit(0)
            self.next_calculator_signal.emit(e_text)  # 다음 예측 단계로 넘어감.

            self.run_calculator = False
            break

    # 헤이딜러 시세 데이터를 추출.
    # dataframe 타입으로 반환.

    def extractHeydealerDB(self):
        # 사용자 설정.
        min_mileage_limit = 2  # 주행거리 간격 설정 (낮은 주행거리)
        max_mileage_limit = 2  # 주행거리 간격 설정 (많은 주행거리)

        min_budder_count = 5  # 입찰자 수 제한 (입찰자 수가 해당 변수값보다 작으면 검색하지 않음)
        not_search_changed_car = False  # 완전무사고 차량을 검색할 때, 단순교환 차량을 검색하지 않는다.
        not_search_accident_car = True  # 유사고 차량을 검색하지 않습니다.

        # 카테고리 데이터를 불러온다.
        # 카테고리 데이터에서 get 코드를 추가한다.
        database_data = None
        db = pymysql.connect(host='grdver.xyz',
                             port=3306,
                             user='healer',
                             password='7974',
                             db='HeyHealer',
                             charset='utf8',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)

        sql = "SELECT * FROM categories WHERE brand = '{}' and model_group = '{}' and model = '{}'".format(
            self.car_data['brand'], self.car_data['model_group'], self.car_data['model'])
        with db:
            with db.cursor() as cur:
                cur.execute(sql)
                database_data = cur.fetchall()

        if database_data == None:
            return []

        is_imported = self.isImported(self.car_data)
        grade_words = self.car_data['grade'].split(' ')
        grade_index = 0
        index_count = 0
        for i, v in enumerate(database_data):
            db_words = v['grade'].split(' ')
            while self.run_calculator:
                try:
                    if grade_words[index_count] == db_words[index_count]:
                        grade_index = i
                        index_count += 1
                    else:
                        break
                except:
                    break

        pd_db_data = pd.DataFrame(database_data)

        url = 'https://dealer.heydealer.com/chart?period=c'
        url += '&' + pd_db_data['brand_code'][grade_index]
        url += '&' + pd_db_data['model_group_code'][grade_index]
        url += '&' + pd_db_data['model_code'][grade_index]
        url += '&' + pd_db_data['grade_code'][grade_index]
        if self.car_data['car_years'] > self.car_data['years']:
            url += '&years=' + str(self.car_data['car_years'])
            url += '&years=' + str(self.car_data['years'])
        elif self.car_data['car_years'] == self.car_data['years']:
            url += '&years=' + str(self.car_data['car_years'])
            url += '&years=' + str(self.car_data['years'] - 1)
        elif self.car_data['car_years'] < self.car_data['years']:
            url += '&years=' + str(self.car_data['car_years'])

        #years_plus_one = self.car_data['years'] + 1
        # if years_plus_one <= datetime.now().year:
        #    url += '&years=' + str(years_plus_one)

        min_mileage = int(
            round(float(self.car_data['mileage']) * 0.0001) - min_mileage_limit)
        if min_mileage < 0:
            min_mileage = 0
        max_mileage = int(
            round(float(self.car_data['mileage']) * 0.0001) + max_mileage_limit)
        url += '&min_mileage=' + str(min_mileage)
        url += '&max_mileage=' + str(max_mileage)
        self.driver.get(url)

        # 헤이딜러 매입시세 리스트 스크롤
        scroll_location = self.driver.execute_script(
            "return document.body.scrollHeight")

        t = 0
        time = 5
        while t < time and self.run_calculator:
            self.driver.execute_script(
                "window.scrollTo(0,document.body.scrollHeight)")

            sleep(2)

            scroll_height = self.driver.execute_script(
                "return document.body.scrollHeight")

            if scroll_location == scroll_height:
                t += 1
                if t >= time:
                    break
            else:
                scroll_location = self.driver.execute_script(
                    "return document.body.scrollHeight")

        # 차량 전체 페이지 html 파싱.
        try:
            page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '''//div[@class="_f52850f"]'''))).get_attribute('innerHTML')
            self.soup = BeautifulSoup(page, 'html.parser')
        except:
            pass

        # _c8685f3
        # 리스트 추출 데이터화.
        elements = self.soup.select('div._c8685f3')
        car_list = []

        if len(elements) > 0:

            for i, element in enumerate(elements, start=1):

                brand = self.car_data['brand']
                model_group = self.car_data['model_group']
                model = self.car_data['model']
                grade = element.select_one('p._adbf321').get_text()

                max_price = element.select_one('p._795af44').get_text()
                max_price = int(re.sub(r'[^0-9]', '', max_price))

                bidder = element.select_one('p._f86efd8').get_text()
                bidder = int(re.sub(r'[^0-9]', '', bidder))

                auc_date = element.select_one('p._6c7f804').get_text()

                car_date = element.select_one(
                    'div._bbdb30b > span > span:nth-child(1)').get_text()
                car_date_years = int(car_date.split('-')[0])
                car_date_month = int(car_date.split('-')[1].split(' ')[0])
                car_years = int(
                    '20' + re.sub(r'[^0-9]', '', car_date.split('-')[1].split(' ')[1]))
                mileage = element.select_one(
                    'div._bbdb30b > span > span:nth-child(2)').get_text()
                mileage = int(re.sub(r'[^0-9]', '', mileage) + "000")
                mission = element.select_one(
                    'div._bbdb30b > span > span:nth-child(3)').get_text()

                try:
                    accident = element.select_one(
                        'div._bbdb30b > span > span:nth-child(4)').get_text()
                    if accident == "교환/판금 없음":
                        accident = "완전무사고"
                    elif accident == "교환/판금 있음":
                        accident = "단순교환"
                    else:
                        accident = None
                except:
                    accident = None

                if accident == None:
                    accident = "유사고"

                click_element = self.driver.find_element_by_xpath(
                    '//div[@class="_c8685f3"][' + str(i) + ']//button[@class="_b1ebced"]')

                self.driver.execute_script(
                    "arguments[0].click();", click_element)

                add = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="_09a6f7d"]'))).get_attribute('innerHTML')
                add_soup = BeautifulSoup(add, 'html.parser')

                options = []
                blue_options = []
                all_options = []
                color_detail = None

                opt_elements = add_soup.select('div._32562f6 > div._7e04722')
                for opt in opt_elements:

                    blue_opt_text = opt.select_one('span._e18aa61._bc2e4c5')
                    if blue_opt_text != None:
                        blue_opt_text = blue_opt_text.get_text()
                        blue_options.append(blue_opt_text)
                        options.append(blue_opt_text)
                        all_options.append(blue_opt_text)

                    normal_opt_text = opt.select_one('span._e18aa61._68b1847')
                    if normal_opt_text != None:
                        normal_opt_text = normal_opt_text.get_text()
                        options.append(normal_opt_text)
                        all_options.append(normal_opt_text)

                    none_opt_text = opt.select_one('span._e18aa61._9e6c379')
                    if none_opt_text != None:
                        none_opt_text = none_opt_text.get_text()
                        all_options.append(none_opt_text)

                opt_data = {}
                opt_data['옵션'] = options
                opt_data['추가옵션'] = blue_options
                opt_data['전체옵션'] = all_options
                json_opt = json.dumps(opt_data, ensure_ascii=False)

                color_detail = add_soup.select_one(
                    'div._96531c5 > div:nth-child(1) > p._050b1fe').get_text()
                car_color = color_detail
                color_datas = MySQL().selectFromTable('colors')
                for color_data in color_datas:
                    if color_data['detail_color'] == color_detail:
                        car_color = color_data['normal_color']

                car_data = {
                    "brand": brand,
                    "model_group": model_group,
                    "model": model,
                    "grade": grade,
                    "max_price": max_price,
                    "selective_price": 0,
                    "bidder": bidder,
                    "end_date": auc_date,
                    "years": car_date_years,
                    "month": car_date_month,
                    "car_years": car_years,
                    "mileage": mileage,
                    "mission": mission,
                    "accident": accident,
                    "json_options": json_opt,
                    "color": car_color,
                    "detail_color": color_detail,
                }

                # 리스트 필터링.
                is_append = True

                # 등급이 다른 차종은 제외.
                if car_data['grade'] != self.car_data['grade']:
                    is_append = False

                # 차량 연식이 맞지 않는 차량 제외.
                if car_data['car_years'] != self.car_data['car_years']:
                    is_append = False

                # 옵션 다른 차량은 제외.
                json_curr_option = json.loads(self.car_data['json_options'])
                json_data_option = json.loads(car_data['json_options'])
                if json_curr_option['전체옵션'] != json_data_option['전체옵션']:
                    is_append = False

                if is_imported:
                    if json_curr_option['옵션'] != json_data_option['옵션']:
                        is_append = False

                # 유사고 차량 제외.
                if not_search_accident_car:  # 유사고 차량을 검색하지 않는 변수가 참이라면...
                    if car_data['accident'] == "유사고":
                        is_append = False

                # 입찰자 수 기준치 이하 삭제.
                if car_data['bidder'] < min_budder_count:
                    is_append = False

                if self.car_data['accident'] == "완전무사고":
                    if not_search_changed_car:  # 완전무사고 차량일 경우 단순교환 차량을 검색하지 않는다면...
                        if car_data['accident'] == "단순교환":
                            is_append = False

                if is_append:
                    car_list.append(car_data)

        if len(car_list) != 0:
            df_data_list = pd.DataFrame(car_list)
            df_data_list = df_data_list.sort_values('max_price')
            car_list = df_data_list.to_dict('records')

        return car_list

    def extractHealerDB(self):

        # 사용자 설정.
        min_mileage_limit = 2  # 주행거리 간격 설정 (낮은 주행거리)
        max_mileage_limit = 2  # 주행거리 간격 설정 (많은 주행거리)

        min_budder_count = 5  # 입찰자 수 제한 (입찰자 수가 해당 변수값보다 작으면 검색하지 않음)
        not_search_changed_car = False  # 완전무사고 차량을 검색할 때, 단순교환 차량을 검색하지 않는다.
        not_search_accident_car = True  # 유사고 차량을 검색하지 않습니다.

        is_imported = self.isImported(self.car_data)

        db_datas = None
        db = pymysql.connect(host='grdver.xyz',
                             port=3306,
                             user='healer',
                             password='7974',
                             db='HeyHealer',
                             charset='utf8',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)

        sql = "SELECT * FROM heydealer_car_data WHERE brand = '{}' and model_group = '{}' and model = '{}' and grade = '{}' and car_years = '{}'".format(
            self.car_data['brand'], self.car_data['model_group'], self.car_data['model'], self.car_data['grade'], self.car_data['car_years'])
        with db:
            with db.cursor() as cur:
                cur.execute(sql)
                db_datas = cur.fetchall()

        if len(db_datas) == 0:
            return []

        return_datas = []
        for index, value in enumerate(db_datas, start=0):

            # 유사고 차량 제외.
            if not_search_accident_car:
                if value['accident'] == "유사고":
                    continue

            if not_search_changed_car:
                if self.car_data['accident'] == "완전무사고":
                    if value['accident'] == "단순교환":
                        continue

            if value['selective_price'] == 0:
                if value['bidder'] < min_budder_count:
                    continue

            if value['mileage'] > self.car_data['mileage'] + (max_mileage_limit * 10000) or value['mileage'] < self.car_data['mileage'] - (min_mileage_limit * 10000):
                continue

            return_datas.append(db_datas[index])

        if len(return_datas) != 0:
            df_data_list = pd.DataFrame(return_datas)
            df_data_list = df_data_list.sort_values('max_price')
            return_datas = df_data_list.to_dict('records')

        return return_datas

    def extractEncar(self):

        is_imported = self.isImported(self.car_data)

        self.driver.get(self.car_data['url'])

        page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '''//div[@class="_87edb25"]'''))).get_attribute('innerHTML')
        self.soup = BeautifulSoup(page, 'html.parser')

        #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="css-zh51te"]'))).click()
        click_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@class="css-zh51te"]')))
        self.driver.execute_script("arguments[0].click();", click_element)
        sleep(1)

        while len(self.driver.window_handles) > 3:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            self.driver.close()
            sleep(1)

        self.driver.switch_to.window(self.driver.window_handles[-1])
        sleep(1)

        """
        original_url = self.driver.current_url
        if original_url.find('http://13.124.139.197/') != -1:
            original_url = str(original_url).split('http://13.124.139.197/')[1]

        if str(original_url).find('Year.range%28') != -1:
            year_split = str(original_url).split('Year.range%28')[1]
            year_split1 = str(year_split).split('%29')[0]
            year_text = 'Year.range%28' + str(year_split1) + '%29'
            new_url = str(original_url).replace(year_text, "Year.range%28{}..{}%29".format(
                str(self.car_data['years']) + "01", str(self.car_data['car_years']) + "12"))
            self.driver.get(new_url)
            sleep(1)

        if str(original_url).find('Mileage.range%28') != -1:
            mileage_split = str(original_url).split('Mileage.range%28')[1]
            mileage_split1 = str(mileage_split).split('%29')[0]
            mileage_text = 'Mileage.range%28' + str(mileage_split1) + '%29'
        """

        try:
            if is_imported == False:

                try:
                    element_count = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="warranty"]/div/ul/li[2]/div/em')))
                    element_int = int(re.sub('[^0-9]', '', element_count.text))
                    if element_int > 0:

                        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                            (By.XPATH, '//label[@for="warranty_1"]'))).click()

                        sleep(1)
                except:
                    pass

            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="fn_sort"]/a[2]'))).click()

            sleep(1)

            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="schset performance"]/h5/a'))).click()

            sleep(1)

            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//label[@for="condition_1"]'))).click()

            sleep(1)

            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//label[@for="condition_2"]'))).click()

            sleep(1)

            sr_normal = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '''//tbody[@id="sr_normal"]'''))).get_attribute('innerHTML')
            self.soup = BeautifulSoup(sr_normal, 'html.parser')

            elements = self.soup.select('tr')
        except:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            return None

        if len(elements) < 2:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            return None

        encar_low_price = None

        for i, v in enumerate(elements):

            #detail_url = v.find("a", class_='newLink _link')['href']
            #self.driver.get("http://www.encar.com/" + detail_url)

            try:
                price_element = v.select_one('td.prc_hs').get_text()
                if price_element.find("리스승계") != -1:
                    continue
                if price_element.find("렌트승계") != -1:
                    continue
                if price_element.find("홈서비스 계약중") != -1:
                    continue
            except:
                continue

            price_text = v.select_one('td.prc_hs > strong').get_text()
            car_years = v.find("span", class_='yer').get_text()

            check_car_years = False

            if self.car_data['car_years'] > self.car_data['years']:
                if int(car_years.split('/')[0]) == int(str(self.car_data['years'])[2:4]):
                    check_car_years = True

            if int(car_years.split('/')[0]) < int(str(self.car_data['years'])[2:4]):
                check_car_years = True

            # 역각자.
            if self.car_data['car_years'] < self.car_data['years']:
                if int(car_years.split('/')[0]) == int(str(self.car_data['car_years'])[2:4]):
                    check_car_years = False

            if check_car_years:
                if car_years.find('년형') == -1:
                    continue
                else:
                    f_text = car_years.split('(')[1]
                    l_text = f_text.split('년형)')[0]
                    if self.car_data['car_years'] != int("20" + str(re.sub(r'[^0-9]', '', l_text))):
                        continue

            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//tbody[@id="sr_normal"]/tr[' + str(i + 1) + ']/td[@class="inf"]/a'))).click()
                sleep(1)
            except:
                continue

            # self.driver.execute_script('window.open("{}");'.format(detail_url))
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)

            # 사고 유무, 교환 판금 확인.
            try:

                car_acc_page = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '''//div[@class="article article_inspect areaScrollCheck"]'''))).get_attribute('innerHTML')
                car_acc_soup = BeautifulSoup(car_acc_page, 'html.parser')

                # 엔카진단.
                accident_text = car_acc_soup.select_one('em.emph_g').get_text()
                if accident_text != "무사고 차량":
                    self.driver.switch_to.window(
                        self.driver.window_handles[-1])
                    sleep(1)
                    self.driver.close()
                    self.driver.switch_to.window(
                        self.driver.window_handles[-1])
                    sleep(1)
                    continue

                changed_element = car_acc_soup.select_one(
                    'ul.list_append > li:nth-child(1) > div.info_append > ul.detail_append > li:nth-child(1) > span.txt_g')
                sheeting_element = car_acc_soup.select_one(
                    'ul.list_append > li:nth-child(1) > div.info_append > ul.detail_append > li:nth-child(2) > span.txt_g')
                corrosion_element = car_acc_soup.select_one(
                    'ul.list_append > li:nth-child(1) > div.info_append > ul.detail_append > li:nth-child(3) > span.txt_g')

                if changed_element == None:
                    self.driver.switch_to.window(
                        self.driver.window_handles[-1])
                    sleep(1)
                    self.driver.close()
                    self.driver.switch_to.window(
                        self.driver.window_handles[-1])
                    sleep(1)
                    continue

                changed_text = changed_element.get_text()
                sheeting_text = sheeting_element.get_text()
                corrosion_text = corrosion_element.get_text()

                changed_count = int(re.sub(
                    r'[^0-9]', '', changed_text)) if re.sub(r'[^0-9]', '', changed_text) != '' else 0
                if changed_count > 2:
                    self.driver.switch_to.window(
                        self.driver.window_handles[-1])
                    sleep(1)
                    self.driver.close()
                    self.driver.switch_to.window(
                        self.driver.window_handles[-1])
                    sleep(1)
                    continue

            except:

                try:  # 엔카 진단 외
                    car_acc_page = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                        (By.XPATH, '''//*[@id="areaPerformance"]'''))).get_attribute('innerHTML')
                    car_acc_soup = BeautifulSoup(car_acc_page, 'html.parser')

                    accident_text = car_acc_soup.select_one('#txtInspAcc').get_text()
                    
                    if accident_text.find("없음") == -1:
                        self.driver.switch_to.window(
                            self.driver.window_handles[-1])
                        sleep(1)
                        self.driver.close()
                        self.driver.switch_to.window(
                            self.driver.window_handles[-1])
                        sleep(1)
                        continue

                    changed_element = car_acc_soup.select_one(
                        '#wrapInsp > div.detail_inspection_info > dl:nth-child(1) > dd > div > span:nth-child(1)')
                    sheeting_element = car_acc_soup.select_one(
                        '#wrapInsp > div.detail_inspection_info > dl:nth-child(1) > dd > div > span:nth-child(2)')
                    corrosion_element = car_acc_soup.select_one(
                        '#wrapInsp > div.detail_inspection_info > dl:nth-child(1) > dd > div > span:nth-child(3)')

                    if changed_element == None:
                        self.driver.switch_to.window(
                            self.driver.window_handles[-1])
                        sleep(1)
                        self.driver.close()
                        self.driver.switch_to.window(
                            self.driver.window_handles[-1])
                        sleep(1)
                        continue

                    changed_text = changed_element.get_text()
                    sheeting_text = sheeting_element.get_text()
                    corrosion_text = corrosion_element.get_text()

                    changed_text = changed_text.split(':')[1].strip()
                    sheeting_text = sheeting_text.split(':')[1].strip()
                    corrosion_text = corrosion_text.split(':')[1].strip()

                    changed_count = int(re.sub(
                        r'[^0-9]', '', changed_text)) if re.sub(r'[^0-9]', '', changed_text) != '' else 0
                    if changed_count > 2:
                        self.driver.switch_to.window(
                            self.driver.window_handles[-1])
                        sleep(1)
                        self.driver.close()
                        self.driver.switch_to.window(
                            self.driver.window_handles[-1])
                        sleep(1)
                        continue

                except:

                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    sleep(1)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    sleep(1)
                    continue


            # 보험 이력 조회.
            try:
                # 엔카진단 전용.
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '''//ul[@class="list_keyinfo"]/li[2]/a[@class="link_g"]'''))).click()

                sleep(1)
            except:
                try:
                    # 엔카진단 외 차량.
                    record_click_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                        (By.XPATH, '''//*[@id="areaBase"]/div[3]/div/div[1]/div[2]/ul/li[2]/div/a''')))
                    self.driver.execute_script(
                        "arguments[0].click();", record_click_element)
                    sleep(1)
                except:
                    self.driver.switch_to.window(
                        self.driver.window_handles[-1])
                    sleep(1)
                    self.driver.close()
                    self.driver.switch_to.window(
                        self.driver.window_handles[-1])
                    sleep(1)
                    continue

            # 보험 이력 조회 새창 열림.
            # 새창으로 전환.
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)

            try:
                record_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '''//body'''))).get_attribute('innerHTML')
                record_soup = BeautifulSoup(record_page, 'html.parser')

                record_element = record_soup.select_one(
                    'div > div.body > div > div.section.sample > div.rreport > div.summary > div.smlist > table > tbody > tr:nth-child(5) > td:nth-child(2)')

                record_text = record_element.get_text().replace(' ', '')
            except:
                # 조회불가차량 오류.
                # 보험 이력 조회 새창 닫기.
                self.driver.switch_to.window(self.driver.window_handles[-1])
                sleep(1)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
                sleep(1)
                continue

            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)

            # 미확정 제한.
            if record_text.find("미확정") != -1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                sleep(1)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
                sleep(1)
                continue

            # 보험 금액 제한.
            if record_text.find("없음") == -1:
                record_text = str(record_text).split('회,')[1]
                record_count = int(re.sub(r'[^0-9]', '', record_text))
            else:
                record_count = 0

            if record_count > 5000000:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                sleep(1)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
                sleep(1)
                continue

            car_name_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//strong[@class="prod_name"]'))).get_attribute('innerHTML')
            car_name_soup = BeautifulSoup(car_name_page, 'html.parser')
            car_name_brand_element = car_name_soup.select_one('span.brand')
            car_name_detail_element = car_name_soup.select_one('span.detail')
            car_brand = car_name_brand_element.get_text()
            car_detail = car_name_detail_element.get_text()
            car_detail = car_detail.strip()

            try:
                car_info_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="carPic"]/div[1]'))).get_attribute('innerHTML')
                info_soup = BeautifulSoup(car_info_page, 'html.parser')

                info_eles = info_soup.select('ul.list_carinfo > li')

                for i, v in enumerate(info_eles):
                    if i == 0:
                        mileage = int(re.sub(r'[^0-9]', '', v.get_text()))

                    if i == 6:
                        color = v.get_text().split('색상:')[1]
            except:
                car_info_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="areaBase"]/div[2]/div[1]/div[2]'))).get_attribute('innerHTML')
                info_soup = BeautifulSoup(car_info_page, 'html.parser')

                info_eles = info_soup.select('ul > li')

                for i, v in enumerate(info_eles):
                    if i == 0:
                        mileage = int(re.sub(r'[^0-9]', '', v.get_text()))

                    if i == 6:
                        color = v.get_text().split('색상:')[1]

            # 추가옵션.
            add_options = ""

            try:
                page_down_element = self.driver.find_element_by_tag_name(
                    'body')
                page_down_element.send_keys(Keys.END)

                add_option_page = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="article article_options areaScrollCheck"]'))).get_attribute('innerHTML')
                add_option_soup = BeautifulSoup(add_option_page, 'html.parser')

                add_option_price_text = add_option_soup.select_one(
                    'em.emph_g').get_text()

                detail_add_option = add_option_soup.select(
                    'dl.option_selection.box_opt > dd')

                add_options_text = ""
                for i, v in enumerate(detail_add_option):
                    try:
                        opt_name = str(
                            detail_add_option[i].select_one('a.link_option'))
                        opt_1 = opt_name.split('</span>')[1]
                        opt_name = opt_1.split('<span')[0]
                    except:
                        try:
                            opt_name = str(
                                detail_add_option[i].select_one('span.link_option'))
                            opt_1 = opt_name.split('</span>')[1]
                            opt_name = opt_1.split('</span')[0]
                        except:
                            continue

                    opt_price = detail_add_option[i].select_one(
                        'span.opt_prc').get_text()
                    add_options_text = add_options_text + \
                        '{}) '.format(str(i + 1)) + opt_name + \
                        " - " + opt_price + "\n"

                add_options = "------------------------------------\n" + \
                    add_option_price_text + " 상당의 선택옵션 장착\n" + add_options_text
            except:
                add_options = "추가 옵션 정보가 없는 엔카 매물입니다"

            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)

            encar_low_price = {"car_brand": car_brand,
                               "car_detail": car_detail,
                               "price": price_text,
                               "car_years": car_years,
                               "mileage": str(format(mileage, ',')),
                               "color": color,
                               "changed": changed_text,
                               "sheeting": sheeting_text,
                               "corrosion": corrosion_text,
                               "my_car_damaged": str(format(record_count, ',')),
                               "add_options": add_options
                               }

            break

        self.driver.switch_to.window(self.driver.window_handles[-1])
        sleep(1)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        sleep(1)

        return encar_low_price

    def deductor(self, car_data):

        # 수입차, 국산차 구분.
        is_imported = self.isImported(car_data)

        config_path = 'healer_config.json'
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        outside_down_price = config_data['Deduct']['imported'][
            'outside'] if is_imported else config_data['Deduct']['domestic']['outside']
        wheel_down_price = config_data['Deduct']['imported'][
            'wheel'] if is_imported else config_data['Deduct']['domestic']['wheel']
        tire_down_price = config_data['Deduct']['imported']['tire'] if is_imported else config_data['Deduct']['domestic']['tire']
        spairkey_down_price = config_data['Deduct']['imported'][
            'spairkey'] if is_imported else config_data['Deduct']['domestic']['spairkey']

        outside_deduct = car_data['scratch_outside'] * outside_down_price
        wheel_deduct = car_data['scratch_wheel'] * wheel_down_price
        tire_deduct = car_data['tire_count'] * tire_down_price

        if car_data['key_count'] < 2:
            spairkey_deduct = (2 - car_data['key_count']) * spairkey_down_price
        else:
            spairkey_deduct = 0

        total_deducts = outside_deduct + wheel_deduct + tire_deduct + spairkey_deduct
        return total_deducts

    def isImported(self, car_data):
        # 수입차/국산차 구분.
        domestic_brands = ['현대', '제네시스', '기아', '쉐보레(GM대우)', '르노삼성', '쌍용', ]

        for d_brand in domestic_brands:
            if d_brand == car_data['brand']:
                return False

        return True
