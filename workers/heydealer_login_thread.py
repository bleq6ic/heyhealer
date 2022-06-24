from time import sleep
from PyQt5.QtCore import *
from selenium import webdriver

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#import chromedriver_autoinstaller
import subprocess
import shutil


class HeydealerLoginThread(QThread):

    status_message_signal = pyqtSignal(str)  # text
    new_heyhealer_signal = pyqtSignal(str)  # id

    def __init__(self, parent, qWidget, heydealer_id, heydealer_pw, is_headless):
        super().__init__()
        self.parent = parent
        self.heydealer_id = heydealer_id
        self.heydealer_pw = heydealer_pw
        self.is_headless = is_headless

        self.run_thread = True

        self.status_message_signal.connect(qWidget.setStatusMessage)
        self.new_heyhealer_signal.connect(self.parent.newHeyhealer)

    def run(self):

        while self.run_thread:
            self.status_message_signal.emit("로그인을 시도중입니다")
            url = "https://dealer.heydealer.com"

            """
            try:
                shutil.rmtree(r"c:\chrometemp")  # 쿠키 / 캐쉬파일 삭제
            except FileNotFoundError:
                pass

            subprocess.Popen(
                r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')  # 디버거 크롬 구동

            options = Options()
            options.add_experimental_option(
                "debuggerAddress", "127.0.0.1:9222")

            chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[
                0]
            try:
                self.driver = webdriver.Chrome(
                    f'./{chrome_ver}/chromedriver.exe', options=options)
            except:
                chromedriver_autoinstaller.install(True)
                self.driver = webdriver.Chrome(
                    f'./{chrome_ver}/chromedriver.exe', options=options)
                    
            self.driver.implicitly_wait(3)

            """
            options = webdriver.ChromeOptions()
            
            if self.is_headless == True:
                options.add_argument("headless")

            # options.add_argument('--no-sandbox')
            # options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option("excludeSwitches", ["enable-logging"])

            self.parent.driver = webdriver.Chrome(options=options)
            self.driver = self.parent.driver
            self.driver.set_window_size(1280, 800)
            #self.driver.maximize_window()
            self.driver.implicitly_wait(3)

            driver = self.driver
            driver.get(url)

            driver.find_element_by_name("username").send_keys(
                self.heydealer_id)
            driver.find_element_by_name("password").send_keys(
                self.heydealer_pw)
            driver.find_element_by_xpath('//button[@class="_eaaa748"]').click()

            sleep(5)  # 정상 로그인 5초 후 확인

            if driver.current_url == "https://dealer.heydealer.com/dashboard":
                self.parent.driver = driver
                self.status_message_signal.emit("로그인에 성공하였습니다")
                self.new_heyhealer_signal.emit(self.heydealer_id)

                try:
                    driver.find_element_by_xpath(
                        '//button[@class="_8476d5e"]').click()
                except:
                    pass

            else:
                self.status_message_signal.emit("로그인에 실패하였습니다")
                self.driver.quit()

            self.run_thread = False
            break
