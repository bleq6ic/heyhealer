from numpy import append
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
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from time import sleep
import time
import json
from sqlalchemy import create_engine
from gui.car_data_gui import CarDataGUI
from selenium.webdriver import ActionChains

from workers.databaser import MySQL

from bs4 import BeautifulSoup


class Crawler(QThread, QObject):
    status_bar_signal_to_widget = pyqtSignal(str)
    progress_signal_to_widget = pyqtSignal(int, int)
    crawler_quit_signal_to_widget = pyqtSignal(int, bool)
    finished_signal_to_widget = pyqtSignal(int)

    start_estimate_signal_to_widget = pyqtSignal()

    show_message_signal = pyqtSignal(str, str)
    window_title_signal = pyqtSignal(str)
    car_data_signal = pyqtSignal(
        str, str, str, str, str, int, int, int, int, str, str, str, str, str, str, str, int)
    deduct_signal = pyqtSignal(int, int, int, str, int, int)
    # int = 0: setText, 1: append, 2:clear
    option_signal = pyqtSignal(int, str)
    add_option_signal = pyqtSignal(int, str)
    # int = 0: setText, 1: append, 2:clear
    new_release_signal = pyqtSignal(int, str)
    accident_signal = pyqtSignal(str, str)
    paint_signal = pyqtSignal(str)
    sheet_metal_signal = pyqtSignal(str)
    changed_signal = pyqtSignal(str)
    accident_repairs_count_signal = pyqtSignal(int, int, int)
    acc_history_signal = pyqtSignal(str, str, int, int, int, str)
    comments_signal = pyqtSignal(str)
    heydealer_comment_signal = pyqtSignal(str)
    auction_signal = pyqtSignal(str, int, str, int, int, int, int, int)
    enable_auction_button_signal = pyqtSignal(bool)

    def __init__(self, parent, heyhealer_parent, crawling_type):

        super().__init__()

        self.parent = parent
        self.heyhealer_parent = heyhealer_parent
        # 0 = url 분석, 2 = 찜종료, 3 = 내입찰 완료
        self.crawling_type = crawling_type
        self.heydealer_id = self.heyhealer_parent.heydealer_id
        self.driver = self.heyhealer_parent.driver
        self.pd_match_accident_repairs = self.parent.pd_match_accident_repairs
        self.pd_categories = self.parent.pd_categories

        # 차량 경고 변수 초기화.
        self.alert = ""

        if self.crawling_type == 0:
            self.process_name = "URL 분석: "
        elif self.crawling_type == 1:
            self.process_name = "관심차량 프로세스: "
        elif self.crawling_type == 2:
            self.process_name = "찜 종료 프로세스: "
        elif self.crawling_type == 3:
            self.process_name = "내입찰 완료 프로세스: "
        else:
            self.process_name = ""

        self.progress_signal_to_widget.connect(
            self.heyhealer_parent.setProgressBar)
        self.status_bar_signal_to_widget.connect(
            self.heyhealer_parent.statusShowMessage)
        self.finished_signal_to_widget.connect(
            self.heyhealer_parent.finishedThread)
        self.crawler_quit_signal_to_widget.connect(
            self.heyhealer_parent.setSingleExecution)
        self.start_estimate_signal_to_widget.connect(
            self.heyhealer_parent.startEstimateHeydealerDB)

        if self.crawling_type == 0:
            self.connectSignalsWithCarDataGUI()  # url 차량 정보 위젯과 시그널 연결.

        self.is_crawler_working = True

    def connectSignalsWithCarDataGUI(self):
        self.car_data_gui = CarDataGUI(self.parent, self.heyhealer_parent)

        # 차량 정보 윈도우 -> 크롤러(this)에게 보내는 시그널 연결.
        self.car_data_gui.close_signal.connect(self.stopCrawling)

        # 크롤러(this) -> 차량 정보 윈도우로 보내는 시그널 연결.
        self.show_message_signal.connect(self.car_data_gui.showMessageBox)
        self.window_title_signal.connect(self.car_data_gui.windowTitle)
        self.car_data_signal.connect(self.car_data_gui.setTextCarData)
        self.deduct_signal.connect(self.car_data_gui.setTextDeductData)
        self.option_signal.connect(
            self.car_data_gui.setTextBrowserOptionData)
        self.add_option_signal.connect(
            self.car_data_gui.setTextBrowserAddOptionData)
        self.new_release_signal.connect(
            self.car_data_gui.setTextBrowserNewReleaseData)
        self.accident_signal.connect(self.car_data_gui.setTextAccidentData)
        self.paint_signal.connect(self.car_data_gui.appendPaintData)
        self.sheet_metal_signal.connect(
            self.car_data_gui.appendSheetMetalData)
        self.changed_signal.connect(self.car_data_gui.appendChangedData)
        self.accident_repairs_count_signal.connect(
            self.car_data_gui.setTextAccidentRepairsCountData)
        self.acc_history_signal.connect(
            self.car_data_gui.setTextAccidentHistory)
        self.comments_signal.connect(self.car_data_gui.setTextComments)
        self.heydealer_comment_signal.connect(
            self.car_data_gui.setTextHeydealerComment)
        self.auction_signal.connect(self.car_data_gui.setTextAuction)
        self.enable_auction_button_signal.connect(
            self.car_data_gui.setEnabledAuctionCalculatorButton)

    def run(self):

        self.crawler_quit_signal_to_widget.emit(self.crawling_type, True)

        while len(self.driver.window_handles) > 1 and self.is_crawler_working:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            self.driver.close()
            sleep(1)

        self.driver.switch_to.window(self.driver.window_handles[0])
        sleep(1)

        while self.is_crawler_working:

            self.runScrolling()
            self.runCrawler()

            break

        self.crawler_quit_signal_to_widget.emit(self.crawling_type, False)

        self.status_bar_signal_to_widget.emit(self.process_name + "종료")
        self.finished_signal_to_widget.emit(self.crawling_type)

    def stop(self):
        self.is_crawler_working = False
        self.quit()
        self.wait(3000)

    def runScrolling(self):
        if self.crawling_type == 1:  # 관심차량.
            page_url = 'https://dealer.heydealer.com/auction/subscription?type=auction&order=recent&is_subscribed=true'
            crawling_xpath = '//a[@class="css-ed692r"]'
        elif self.crawling_type == 2:  # 찜차량(종료).
            page_url = 'https://dealer.heydealer.com/auction/starred_end?type=star&order=recent&auction_status=expired&auction_status=ended'
            crawling_xpath = '//a[@class="css-ed692r"]'
        elif self.crawling_type == 3:  # 내입찰 완료.
            page_url = 'https://dealer.heydealer.com/bid/my_bids_expired?type=bid&auction_status=expired&order=recent'
            crawling_xpath = '//a[@class="_655d8ab undefined"]'
        elif self.crawling_type == 4:
            page_url = 'https://dealer.heydealer.com/auction/starred?type=star&order=recent&auction_status=approved'
            crawling_xpath = '//a[@class="css-ed692r"]'

        while self.is_crawler_working:

            self.car_links = []

            if self.crawling_type != 0:

                """ 페이지 스크롤 시작 """

                # 최대 대기시간.
                max_wait_time = self.heyhealer_parent.wait_scroll_time

                driver = self.driver
                driver.get(page_url)

                self.status_bar_signal_to_widget.emit(
                    self.process_name + "목록 확인 중")

                prev_car_list = 0

                t = 0
                time = max_wait_time

                while t < time and self.is_crawler_working:

                    prev_car_list = driver.find_elements_by_xpath(
                        crawling_xpath)

                    if len(prev_car_list) == 0:
                        sleep(1)
                        t += 1
                    else:
                        break

                if len(prev_car_list) == 0:
                    self.is_crawler_working = False
                    break

                while self.is_crawler_working:

                    t = 0.0
                    time = max_wait_time
                    input_time = 0.2
                    while t < time and self.is_crawler_working:
                        #self.action = ActionChains(driver)
                        # self.action.move_to_element(prev_car_list[-1]).perform()
                        page_down_element = driver.find_element_by_tag_name(
                            'body')
                        page_down_element.send_keys(Keys.END)

                        sleep(input_time)

                        curr_car_list = driver.find_elements_by_xpath(
                            crawling_xpath)

                        if len(curr_car_list) == len(prev_car_list):
                            t += input_time
                        else:
                            break

                    if self.heyhealer_parent.is_limit_scroll:
                        if len(curr_car_list) > self.heyhealer_parent.limit_scroll_count:
                            break

                    if len(prev_car_list) == len(curr_car_list):
                        break
                    else:
                        prev_car_list = driver.find_elements_by_xpath(
                            crawling_xpath)

                car_list = driver.find_elements_by_xpath(crawling_xpath)

                """ 페이지 스크롤 끝 """

                if self.crawling_type == 1:

                    favorite_page = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                        (By.XPATH, '//div[@class="_3f14541"]'))).get_attribute('innerHTML')
                    page_soup = BeautifulSoup(favorite_page, 'html.parser')

                    a_elements = page_soup.select('a.css-ed692r')

                    for i, v in enumerate(a_elements, start=1):
                        try:
                            heart_path = a_elements[i -
                                                    1].select_one('svg > path')
                            if heart_path['fill'] == "#272E40":
                                self.car_links.append(
                                    "https://dealer.heydealer.com" + a_elements[i - 1]['href'])
                        except:
                            continue

                else:
                    for i, v in enumerate(car_list):
                        self.car_links.append(
                            car_list[i].get_attribute('href'))

            else:
                self.car_links = [self.heyhealer_parent.car_url]

            break

    def mysqlFindUrl(self, url):
        db = pymysql.connect(host='grdver.xyz',
                             user='healer',
                             password='7974',
                             db='HeyHealer',
                             charset='utf8')

        if self.crawling_type == 2 or self.crawling_type == 3:  # 찜 종료, 내입찰 완료
            sql = "SELECT * FROM heydealer_car_data WHERE url = %s"

        try:
            with db:
                with db.cursor() as cur:
                    cur.execute(sql, (url))
                    return cur.fetchall()
        except:
            return None

    def runCrawler(self):

        for i, v in enumerate(self.car_links, start=1):
            if self.is_crawler_working == False:
                break

            if i > self.heyhealer_parent.crawling_start_index:
                self.crawling(v)

            progress_value = int(i / len(self.car_links) * 100)

            self.progress_signal_to_widget.emit(
                self.crawling_type, progress_value)

            if self.alert != "":
                self.show_message_signal.emit("경고", self.alert)

            if self.crawling_type != 0:
                self.status_bar_signal_to_widget.emit(
                    self.process_name + "차량을 저장중 (" + str(i) + " / " + str(len(self.car_links)) + ")")

        self.stopCrawling()

    def selectOneParser(self, select_path):
        return self.soup.select_one(select_path).get_text() if self.soup.select_one(select_path) != None else "None"

    def crawling(self, url):

        if self.crawling_type == 2 or self.crawling_type == 3:

            if len(self.mysqlFindUrl(url)) != 0:
                return

        self.url = url

        while self.is_crawler_working:

            while len(self.driver.window_handles) > 1 and self.is_crawler_working:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                sleep(1)
                self.driver.close()
                sleep(1)

            self.driver.switch_to.window(self.driver.window_handles[0])
            sleep(1)

            self.driver.execute_script('window.open("{}");'.format(self.url))
            self.driver.switch_to.window(self.driver.window_handles[-1])
            sleep(1)
            # self.driver.get(self.url)

            # 차량 전체 페이지 html 파싱.
            try:

                page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '''//div[@class="_87edb25"]'''))).get_attribute('innerHTML')
                self.soup = BeautifulSoup(page, 'html.parser')

            except:

                break

            # 관심차량 찜이라면, 찜버튼을 누르고 종료.
            if self.crawling_type == 1:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="css-ew39mh"]'))).click()
                sleep(1)
                break

            self.alert = ""

            """ 차량 번호 입력 """

            # 차량번호.
            self.car_number = self.selectOneParser(
                'button._f738231').split(' ')[0]

            """ 차량 번호 입력 완료 """

            """ 경매 정보 입력 """

            # 경매 타입 (경매중, 선택중, 경매종료 등..)
            self.auction_text = self.selectOneParser('h5.css-1mio3z5')
            self.auction_status = "경매종료" if self.auction_text == "None" else self.auction_text

            self.selective_price = 0
            self.max_price = 0
            self.my_price = 0
            self.current_bidder = 0
            self.left_time = ""
            self.bidder = 0
            self.end_date = 0
            end_date_int = -1

            # 경매 정보에 따라 크롤링을 중단시킨다.
            if self.crawling_type == 1:
                if self.auction_status == "경매진행중":

                    try:
                        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '''//path[@d="M11.0082 5.89322C11.6694 6.48067 12 7.14146 12 7.14146C12 7.14146 12.3306 6.48067 12.9918 5.89322C13.5209 5.42313 14.2618 5 15.2143 5C18.4286 5 19.5 8.21219 19.5 9.91679C19.5 15.7073 12.8486 18.9195 12 18.9195C11.1525 18.9195 4.5 15.7073 4.5 9.91679C4.5 8.21219 5.57143 5 8.78571 5C9.73824 5 10.4791 5.42313 11.0082 5.89322ZM12 4.76812C12.713 4.13679 13.7882 3.5 15.2143 3.5C17.4163 3.5 18.9216 4.6381 19.815 5.99376C20.6679 7.28803 21 8.81345 21 9.91679C21 13.4253 18.9842 16.0542 17.0483 17.7251C16.0682 18.5711 15.0608 19.2157 14.2294 19.654C13.8137 19.8731 13.4269 20.0487 13.0949 20.1738C12.8364 20.2712 12.4085 20.4195 12 20.4195C11.5914 20.4195 11.1635 20.2711 10.9053 20.1737C10.5734 20.0486 10.1866 19.8731 9.77106 19.654C8.93969 19.2157 7.93226 18.5711 6.95211 17.7251C5.01621 16.0543 3 13.4254 3 9.91679C3 8.81345 3.33208 7.28803 4.18502 5.99376C5.07843 4.6381 6.58374 3.5 8.78571 3.5C10.2118 3.5 11.287 4.13679 12 4.76812Z"]'''))).click()
                    except:
                        pass
                else:

                    break

            elif self.crawling_type == 2 or self.crawling_type == 3:
                if self.auction_status != "경매종료" and self.auction_status != "유효기간만료":
                    break

            if self.auction_status == "경매종료" or self.auction_status == "유효기간만료":

                if self.auction_status == "유효기간만료":

                    # 최고가
                    max_price_text = self.selectOneParser(
                        'div._2ff649e > div:nth-child(2) > div._4741b49')
                    max_price_text = re.sub(
                        r'[^0-9]', '', max_price_text)
                    self.max_price = int(
                        max_price_text) if max_price_text != "" else 0

                    # 내견적
                    my_price_text = self.selectOneParser(
                        'div._2ff649e > div:nth-child(3) > div._4741b49')
                    my_price_text = re.sub(r'[^0-9]', '', my_price_text)
                    self.my_price = int(
                        my_price_text) if my_price_text != "" else 0

                elif self.auction_status == "경매종료":

                    # 선택가
                    selective_price_text = self.selectOneParser(
                        'span._fde4aa8')
                    selective_price_text = re.sub(
                        r'[^0-9]', '', selective_price_text)
                    self.selective_price = int(
                        selective_price_text) if selective_price_text != "" else 0

                    # 최고가
                    max_price_text = self.selectOneParser(
                        'div._2ff649e > div:nth-child(2) > div._4741b49')
                    max_price_text = re.sub(r'[^0-9]', '', max_price_text)
                    self.max_price = int(
                        max_price_text) if max_price_text != "" else self.selective_price

                    my_price_text = self.selectOneParser(
                        'div._2ff649e > div:nth-child(3) > div._4741b49')
                    my_price_text = re.sub(r'[^0-9]', '', my_price_text)
                    self.my_price = int(
                        my_price_text) if my_price_text != "" else 0

                bidder_text = self.selectOneParser('span._7936899')
                bidder_text = re.sub(r'[^0-9]', '', bidder_text)
                self.bidder = int(
                    bidder_text) if bidder_text != "" else 0

                end_date_int = self.selectOneParser(
                    'div._56d8750 > div._b741ca3')
                end_date_int = re.sub(r'[^0-9]', '', end_date_int)
                self.end_date = int(
                    end_date_int) if end_date_int != "" else "unknown"

                # 경매종료일이 표시되어있지 않다면 오늘 날짜로 지정.
                if self.end_date == "unknown":
                    end_date_int = -1
                    now_time = datetime.now()
                    self.end_date = int(
                        str(now_time.year) + str(now_time.month).zfill(2) + str(now_time.day).zfill(2))
                else:
                    end_date_int = self.end_date
            else:

                self.left_time = self.selectOneParser('div.css-381v83 > p')

                current_bidder_text = self.selectOneParser(
                    'div.css-zjik7 > div:nth-child(1) > div > h5')
                current_bidder_text = re.sub(
                    r'[^0-9]', '', current_bidder_text)
                self.current_bidder = int(
                    current_bidder_text) if current_bidder_text != "" else "unknown"

            self.auction_signal.emit(self.auction_status, self.current_bidder, self.left_time,
                                     self.bidder, end_date_int, self.selective_price, self.max_price, self.my_price)

            """ 경매 정보 입력 완료 """

            """ 차량 기본 정보 입력 """

            self.imported_brands = ['BMW', '벤츠', '아우디', '폭스바겐', '미니', '인피니티', '렉서스', '닛산', '닷지', '도요타', '람보르기니', '랜드로버',
                                    '롤스로이스', '링컨', '마세라티', '맥라렌', '미쯔비시', '벤틀리',
                                    '볼보', '북기은상', '사브', '쉐보레', '스마트', '스바루', '시트로엥', '이스즈', '재규어', '지프', '캐딜락', '크라이슬러',
                                    '테슬라', '페라리', '포드', '포르쉐', '폰티악', '푸조', '피아트', '험머', '혼다']

            self.domestic_brands = ['현대', '제네시스',
                                    '기아', '쉐보레(GM대우)', '르노삼성', '쌍용', ]

            model_full = self.selectOneParser('div._a126993')

            # 등급.
            self.grade = self.selectOneParser('span._076da84')

            # 윈도우 타이틀 시그널.
            self.window_title_signal.emit(model_full + " " + self.grade)

            # 메인 상태바 시그널.
            self.status_bar_signal_to_widget.emit(
                model_full + " " + self.grade)

            # 수입차와 국산차를 구분.
            # 수입차와 국산차는 표기 내용이 다름.

            self.imported = False
            for imported_brand_name in self.imported_brands:
                if model_full.split(' ', 1)[0] == imported_brand_name:
                    self.imported = True
                    self.imported_brand = imported_brand_name
                    break

            if self.imported:
                model_full = model_full.split(' ', 1)[1]

            # 카테고리 데이터를 확인하여 제조사, 모델, 모델상세 설정.
            for i in self.pd_categories.index:
                if self.pd_categories['model'][i] == model_full:
                    self.brand = self.pd_categories['brand'][i]
                    self.model_group = self.pd_categories['model_group'][i]
                    self.model = self.pd_categories['model'][i]
                    break

            # 색상상세.
            self.detail_color = self.selectOneParser('div._86556e8')

            # 차량 원부 클릭.
            try:
                self.driver.find_element_by_xpath(
                    '//button[@class="_f738231"]').click()

                # 차량 원부 페이지 html 파싱.
                car_data_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '''//div[@class="_d9d4866 _803e5ba"]'''))).get_attribute('innerHTML')
                self.car_data_soup = BeautifulSoup(
                    car_data_page, 'html.parser')

                self.color = "unknown"
                car_data_elements = self.car_data_soup.select('div._1776d97')
                for car_data_element in car_data_elements:
                    if car_data_element.get_text().find("색상") != -1:
                        color_text = car_data_element.text.replace(
                            '색상', '').replace('\n', '')
                        self.color = color_text

                self.driver.find_element_by_xpath(
                    '//button[@class="_d85fb4b"]').click()
            except:
                self.color = self.detail_color

            # 최초등록일(년).
            self.years_text = self.selectOneParser(
                'div._76ecded > div > p:nth-child(1) > b')
            self.years = int(re.sub(r'[^0-9]', '', self.years_text)
                             ) if self.years_text != "None" else "unknown"

            # 최초등록일(월).
            self.month_text = self.selectOneParser(
                'div._76ecded > div > p:nth-child(2) > b')
            self.month = int(re.sub(r'[^0-9]', '', self.month_text)
                             ) if self.month_text != "None" else "unknown"

            # 연식.
            self.car_years_text = self.selectOneParser(
                'div._76ecded._f15d9c0 > b')
            self.car_years = int(re.sub(r'[^0-9]', '', self.car_years_text)
                                 ) if self.car_years_text != "None" else "unknown"

            # 주행거리.
            self.mileage_text = self.selectOneParser(
                'div._e9d516b > div:nth-child(3) > div > b')
            self.mileage = int(re.sub(r'[^0-9]', '', self.mileage_text)
                               ) if self.mileage_text != "None" else "unknown"

            # 연료. 변속기.
            fuel_mission = self.selectOneParser('div._43a996f._a182680')
            self.fuel = fuel_mission.split('ㆍ')[0]
            self.mission = fuel_mission.split('ㆍ')[1]

            # 현금/리스.
            self.lease_text = self.selectOneParser(
                'div._43a996f._a6be9ee._dd16fc5').replace('?', '').strip('\n')
            self.lease = "현금" if self.lease_text == "None" else self.lease_text

            # 시트.
            self.seat = self.selectOneParser(
                'div._e9d516b > div:nth-child(2) > div:nth-child(3)')

            # 지역.
            self.region = self.selectOneParser(
                'div._e9d516b > div:nth-child(2) > div._43a996f')

            # 신차가.
            self.car_new_price = 0
            car_new_price_text = self.selectOneParser('div._23e6130')
            if car_new_price_text.find("출고가") != -1:
                start_index = car_new_price_text.find(" : ")
                end_index = start_index + 10
                pr_text = re.sub(
                    r'[^0-9]', '', car_new_price_text[start_index:end_index])
                self.car_new_price = int(pr_text)

            # 차량 정보 이벤트 호출.
            self.car_data_signal.emit(self.car_number,
                                      self.brand,
                                      self.model_group,
                                      self.model,
                                      self.grade,
                                      self.years,
                                      self.month,
                                      self.car_years,
                                      self.mileage,
                                      self.color,
                                      self.detail_color,
                                      self.fuel,
                                      self.mission,
                                      self.seat,
                                      self.lease,
                                      self.region,
                                      self.car_new_price
                                      )

            """ 차량 기본 정보 입력 완료 """

            """ 정비 (감가 내역 ) 입력 """

            # div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)
            # div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)
            # div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2)
            # div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)

            # 외판 손상.
            self.scratch_outside_text = self.selectOneParser(
                'div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)')
            self.scratch_outside_number_text = re.sub(
                r'[^0-9]', '', self.scratch_outside_text)
            self.scratch_outside = int(
                self.scratch_outside_number_text) if self.scratch_outside_number_text != "" else 0

            # 휠 손상.
            self.scratch_wheel_text = self.selectOneParser(
                'div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)')
            self.scratch_wheel_number_text = re.sub(
                r'[^0-9]', '', self.scratch_wheel_text)
            self.scratch_wheel = int(
                self.scratch_wheel_number_text) if self.scratch_wheel_number_text != "" else 0

            # 타이어
            self.tire_detail = self.selectOneParser(
                'div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2)')

            # 손상 타이어 갯수.
            exist_tire = self.selectOneParser('div._9fd3373._4e8b9c4')
            if exist_tire != "None":
                count_text = re.sub(r'[^0-9]', '', exist_tire)
                self.tire_count = 1 if count_text == "" else int(count_text)
            else:
                self.tire_count = 0

            # 보조키, 특수키
            key_or_spair = self.selectOneParser(
                'div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1)')
            self.special_key_index = 0  # 0:적용안됨, 1:없음, 2:있음
            if key_or_spair == "보조키":
                spair_key = self.selectOneParser('div._1d27cd1')
                spair_key_text = spair_key.split(' ')[0]
                self.key_count = 2 if spair_key != "None" and spair_key_text != "없음" else 1
            elif key_or_spair == "차 키":
                key_count_text = self.selectOneParser('div._d8e7bad')
                self.key_count = int(re.sub(r'[^0-9]', '', key_count_text))
                special_key = self.selectOneParser('span._9ed8427')
                self.special_key_index = 2 if special_key.find(
                    "O") != -1 else 1
            else:
                self.key_count = 1

            self.deduct_signal.emit(self.scratch_outside, self.scratch_wheel, self.tire_count,
                                    self.tire_detail, self.key_count, self.special_key_index)

            """ 정비 (감가 내역) 입력 완료 """

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

            self.option_signal.emit(0, self.text_options)

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

            self.add_option_signal.emit(0, self.text_add_options)

            self.opt_list = {"옵션": self.options,
                             "추가옵션": self.add_options, "전체옵션": self.all_options}
            self.json_options = json.dumps(self.opt_list, ensure_ascii=False)

            """ 옵션 입력 완료 """

            """ 출고 정보 입력 """

            new_releases = self.soup.select_one('div._23e6130')
            self.new_release = ""
            if new_releases != None:
                re_child = new_releases.parent.find_all('div')
                for value in re_child:
                    self.new_release = self.new_release + value.get_text() + "\n"

            self.new_release_signal.emit(0, self.new_release)

            """ 출고 정보 입력 완료 """

            """ 성능기록부 입력 """

            self.accident_writer = self.selectOneParser(
                'div._29b7630 > div:nth-child(1) > div._59324d2')
            self.accident = self.selectOneParser(
                'div._29b7630 > div:nth-child(1) > h1')

            self.accident_signal.emit(self.accident_writer, self.accident)

            """ 성능기록부 입력 완료 """

            """ 도색, 판금, 교체 입력 """

            # 사고부위

            # 도색
            acc_paint = self.soup.select('button._531c897._106c669')

            acc_paint_arr = []
            if acc_paint != None:
                for value in acc_paint:
                    t = re.sub(r'[^0-9|,]', '', value['style'])
                    changed_position = []
                    for i, value in enumerate(t.split(',')):
                        changed_position.append(int(value))

                    for index in self.pd_match_accident_repairs.index:
                        if self.pd_match_accident_repairs['position'][index][0] != changed_position[0]:
                            continue
                        if self.pd_match_accident_repairs['position'][index][1] != changed_position[1]:
                            continue

                        changed_text = self.pd_match_accident_repairs['part_display'][index]
                        acc_paint_arr.append(changed_text)
                        self.paint_signal.emit(changed_text)  # 시그널
                        break

            # 판금
            acc_sheet_metal = self.soup.select('button._531c897._1194761')

            acc_sheet_metal_arr = []
            if acc_sheet_metal != None:
                for value in acc_sheet_metal:
                    t = re.sub(r'[^0-9|,]', '', value['style'])
                    changed_position = []
                    for i, value in enumerate(t.split(',')):
                        changed_position.append(int(value))

                    for index in self.pd_match_accident_repairs.index:
                        if self.pd_match_accident_repairs['position'][index][0] != changed_position[0]:
                            continue
                        if self.pd_match_accident_repairs['position'][index][1] != changed_position[1]:
                            continue

                        changed_text = self.pd_match_accident_repairs['part_display'][index]
                        acc_sheet_metal_arr.append(changed_text)
                        self.sheet_metal_signal.emit(changed_text)  # 시그널
                        break

            # 교환
            acc_changed = self.soup.select('button._531c897._56659f8')

            acc_changed_arr = []
            if acc_changed != None:
                for value in acc_changed:
                    t = re.sub(r'[^0-9|,]', '', value['style'])
                    changed_position = []
                    for i, value in enumerate(t.split(',')):
                        changed_position.append(int(value))

                    for index in self.pd_match_accident_repairs.index:
                        if self.pd_match_accident_repairs['position'][index][0] != changed_position[0]:
                            continue
                        if self.pd_match_accident_repairs['position'][index][1] != changed_position[1]:
                            continue

                        changed_text = self.pd_match_accident_repairs['part_display'][index]
                        acc_changed_arr.append(changed_text)
                        self.changed_signal.emit(changed_text)  # 시그널
                        break

            self.accident_repairs = {
                "도색": acc_paint_arr, "판금": acc_sheet_metal_arr, "교환": acc_changed_arr}
            self.json_accident_repairs = json.dumps(
                self.accident_repairs, ensure_ascii=False)

            self.accident_repairs_count_signal.emit(
                len(acc_paint_arr), len(acc_sheet_metal_arr), len(acc_changed_arr))

            """ 도색, 판금, 교환 입력 완료 """

            """ 보험이력 입력 """
            # 용도이력
            usage_history_text = self.selectOneParser(
                'div._18b0841 > div:nth-child(1) > div:nth-child(1) > span._8ca62e8._7c74482')
            self.usage_history = "없음" if usage_history_text == "None" else usage_history_text
            self.alert = self.alert + \
                str(usage_history_text) + \
                "\n" if usage_history_text != "None" else self.alert

            # 침수, 전손
            flooding_loss_text = self.selectOneParser(
                'div._18b0841 > div:nth-child(1) > div:nth-child(2) > span._8ca62e8._7c74482')
            self.flooding_loss = "없음" if flooding_loss_text == "None" else flooding_loss_text
            self.alert = self.alert + \
                str(flooding_loss_text) + \
                "\n" if flooding_loss_text != "None" else self.alert

            # 내차피해 보험이력
            self.total_my_car_damage = 0
            my_car_damage_list = []
            # heydealer > div > div._1f8b15e > div._e32a2db > div > div._6a6e788 > div._c5d3598 > div > div._c5d3598 > div._1b9e8e6 > div > div._82ce12b > div._18b0841 > div:nth-child(3)

            my_history_prices = self.soup.select_one(
                'div._18b0841 > div:nth-child(3) > div._dfeae33')

            if my_history_prices != None:
                my_damaged_price_text_list = []
                child_list = my_history_prices.find_all(
                    'div', {'class': '_903baf7'})

                for value in child_list:
                    price_text = value.select_one('div._e592cd9 > span:nth-child(2) > span').get_text(
                    ) if value.select_one('div._e592cd9 > span:nth-child(2) > span') != None else ""
                    my_damaged_price_text_list.append(price_text)

                for i, value in enumerate(my_damaged_price_text_list):
                    if value == "미확정":
                        self.alert = self.alert + '미확정\n'
                    m_price = re.sub(r'[^0-9]', '', value)
                    m_price = m_price if m_price != '' else 0
                    self.total_my_car_damage = self.total_my_car_damage + \
                        int(m_price)
                    my_car_damage_list.append(int(m_price))

            damaged_list = {"내차피해액": my_car_damage_list}
            self.json_my_car_damaged = json.dumps(
                damaged_list, ensure_ascii=False)

            # 타차가해 보험이력
            self.total_another_blow = 0
            history_prices = self.soup.select_one(
                'div._18b0841 > div:nth-child(4) > div._dfeae33')

            if history_prices != None:
                another_price_text_list = []
                child_list = history_prices.find_all(
                    'div', {'class': '_903baf7'})

                for value in child_list:
                    price_text = value.select_one('div._e592cd9 > span:nth-child(2) > span').get_text(
                    ) if value.select_one('div._e592cd9 > span:nth-child(2) > span') != None else ""
                    another_price_text_list.append(price_text)

                for i, value in enumerate(another_price_text_list):
                    if value == "미확정":
                        self.alert = self.alert + '미확정\n'
                    m_price = re.sub(r'[^0-9]', '', value)
                    m_price = m_price if m_price != '' else 0
                    self.total_another_blow = self.total_another_blow + \
                        int(m_price)

            # 소유자변경
            change_owner_text = self.selectOneParser('h1._656b86f > span')
            change_owner_number_text = re.sub(r'[^0-9]', '', change_owner_text)
            self.change_owner = 0 if change_owner_number_text == "" else int(
                change_owner_number_text)

            # 보험 상세 이력
            acc_history_elements = self.soup.select_one(
                'div._18b0841').find_all('span')
            self.acc_history = ""
            if acc_history_elements != None:
                for value in acc_history_elements:
                    self.acc_history = self.acc_history + value.get_text() + '\n'

            self.acc_history_signal.emit(self.usage_history, self.flooding_loss,
                                         self.total_my_car_damage, self.total_another_blow, self.change_owner,
                                         self.acc_history)

            """ 보험이력 입력 완료 """

            """ 코멘트 입력 """

            comment_elements = self.soup.select('div._fae8a71')
            self.comments = ""
            if comment_elements != None:
                for element in comment_elements:
                    c_element = element.find_all('div')
                    for value in c_element:
                        self.comments = self.comments + value.get_text() + '\n\n'

            self.comments_signal.emit(self.comments)

            """ 코멘트 입력 완료 """

            """ 헤이딜러 코멘트 입력 """

            self.heydealer_comment = self.selectOneParser(
                'div._e59515f > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)')
            if self.heydealer_comment.find("중고차 딜러 업로드 차량") != -1:
                self.alert = self.alert + "중고차 딜러 업로드 차량\n"

            self.heydealer_comment_signal.emit(self.heydealer_comment)

            """ 헤이딜러 코멘트 입력 완료 """

            """ 자료 > 데이터프레임 """

            # 데이터베이스 저장. 찜종료차량, 입찰완료차량만 저장.
            self.saveDatabase(self.crawledData())

            # 추후 분석을 위해서 heyhealer 창에 현재 데이터 저장.
            self.heyhealer_parent.curr_car_data = self.crawledData()

            if self.crawling_type == 0:  # URL 분석 적용.
                self.enable_auction_button_signal.emit(True)

            elif self.crawling_type == 2:  # 찜 종료 차량.
                # 정보가 없거나 저장된 자료는 찜 해제.
                if self.auction_status == "유효기간만료":
                    try:
                        WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@class="css-giwk5h"]'))).click()
                        #self.driver.execute_script("arguments[0].click();", click_element)
                        sleep(1)
                    except:
                        pass
                elif self.auction_status == "경매종료":
                    try:
                        self.driver.switch_to.window(
                            self.driver.window_handles[0])
                        sleep(1)

                        page = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                            (By.XPATH, '//div[@class="_3f14541"]'))).get_attribute('innerHTML')
                        page_soup = BeautifulSoup(page, 'html.parser')

                        a_elements = page_soup.select('a.css-ed692r')

                        valid_index = None
                        for i, v in enumerate(a_elements, start=1):
                            if str(self.url).find(v['href']) != -1:
                                valid_index = i
                                break

                        click_xpath = '//div[@class="_3f14541"]/a[{}]/div[@class="css-e7aqk4"]/div[@class="css-1m05fw1"]/div[@class="css-1wx8zlz"]/div[@class="css-1qh2ioq"]'.format(
                            str(valid_index))
                        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                            (By.XPATH, click_xpath))).click()
                        sleep(1)
                        self.driver.switch_to.window(
                            self.driver.window_handles[-1])
                        sleep(1)
                    except:
                        pass

            elif self.crawling_type == 4:  # 찜목록 입찰 적용.
                # 헤이딜러 매입시세 예상가 쓰레드 시작.
                self.start_estimate_signal_to_widget.emit()
                self.wait_calculator = True
                while self.wait_calculator and self.is_crawler_working:
                    sleep(1)

            break

    @pyqtSlot()
    def stopCrawling(self):
        if self.is_crawler_working:
            self.status_bar_signal_to_widget.emit(self.process_name + " 중단")
        else:
            return

        self.is_crawler_working = False

        if self.crawling_type != 0:
            return

    def crawledData(self):
        # 경매 종료일이 표시되지 않았다면 오늘로 표기.

        return {'auction_status': self.auction_status,
                'brand': self.brand,
                'model_group': self.model_group,
                'model': self.model,
                'grade': self.grade,
                'years': self.years,
                'month': self.month,
                'car_years': self.car_years,
                'color': self.color,
                'detail_color': self.detail_color,
                'mileage': self.mileage,
                'fuel': self.fuel,
                'mission': self.mission,
                'accident': self.accident,
                'accident_writer': self.accident_writer,
                'json_accident_repairs': self.json_accident_repairs,
                'acc_history': self.acc_history,
                'json_my_car_damaged': self.json_my_car_damaged,
                'text_options': self.text_options,
                'text_add_options': self.text_add_options,
                'json_options': self.json_options,
                'new_release': self.new_release,
                'region': self.region,
                'car_new_price': self.car_new_price,
                'lease': self.lease,
                'seat': self.seat,
                'scratch_outside': self.scratch_outside,
                'scratch_wheel': self.scratch_wheel,
                'tire_count': self.tire_count,
                'tire_detail': self.tire_detail,
                'key_count': self.key_count,
                'special_key_index': self.special_key_index,
                'comments': self.comments,
                'heydealer_comment': self.heydealer_comment,
                'car_number': self.car_number,
                'url': self.url,
                'selective_price': self.selective_price,
                'max_price': self.max_price,
                'my_price': self.my_price,
                'end_date': self.end_date,
                'bidder': self.bidder,
                'usage_history': self.usage_history,
                'flooding_loss': self.flooding_loss,
                'total_my_car_damage': self.total_my_car_damage,
                'total_another_blow': self.total_another_blow,
                'change_owner': self.change_owner,
                'alert': self.alert
                }

    def saveDatabase(self, car_data):

        if self.is_crawler_working == False:
            return

        if self.crawling_type == 1 or self.crawling_type == 4:
            return

        if self.crawling_type == 0 or self.crawling_type == 2 or self.crawling_type == 3:

            if car_data['auction_status'] == "경매종료" or car_data['auction_status'] == "유효기간만료":
                table_name = 'heydealer_car_data'
            else:
                return

            # 선택가 또는 최고가 둘다 없는 자료는 필요하지 않으므로 리턴.
            if car_data['selective_price'] == 0 and car_data['max_price'] == 0:
                return

        if len(MySQL().selectWhereColumn(table_name, 'car_number', car_data['car_number'])) > 0:
            return

        engine = create_engine("mysql+pymysql://healer:" + "7974" +
                               "@grdver.xyz/HeyHealer", encoding='utf-8')

        conn = engine.connect()

        df_mysql_data = pd.DataFrame([car_data])
        df_mysql_data.to_sql(name=table_name, con=engine,
                             if_exists='append', index=False)

        # 자세한 색상을 저장.
        if car_data['color'] != "-":
            if len(MySQL().selectWhereColumn('colors', 'detail_color', car_data['detail_color'])) < 1:
                color_data = {"normal_color": car_data['color'],
                              "detail_color": car_data['detail_color']}
                pd_color_data = pd.DataFrame([color_data])
                pd_color_data.to_sql(
                    name='colors', con=engine, if_exists='append', index=False)

        conn.close()

    @pyqtSlot(bool)
    def setWaitCalculator(self, value):
        self.wait_calculator = value
