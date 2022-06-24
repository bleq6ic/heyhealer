from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

from workers.crawler import Crawler
from workers.process import Process
from workers.estimate_calculator import EstimateCalculator
from workers.input_estimate_price import InputEstimate

form_class = uic.loadUiType("designer/heyhealer.ui")[0]

class HeyHealer(QMainWindow, form_class):

    finished_favorite_signal = pyqtSignal()
    finished_favorite_ended_signal = pyqtSignal()
    finished_auction_ended_signal = pyqtSignal()

    finished_input_estimate_signal = pyqtSignal(bool)

    curr_car_data = None

    def __init__(self, parent, driver, heydealer_id):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.driver = driver
        self.heydealer_id = heydealer_id

        self.crawler = None
        self.is_full_process = False
        self.car_url = ""

        self.setUi()

    def setUi(self):

        self.q_user_name.setText(self.heydealer_id)

        """ 버튼 연결 """
        # 프로세스.
        # 프로세스 시작.
        self.q_process_start_button.clicked.connect(self.startProcess)
        self.q_process_stop_button.clicked.connect(self.stopProcess) # 프로세스 중지.

        # 관심차량 찡.
        # 관심차량 찜 시작.
        self.q_favorite_start_button.clicked.connect(lambda: self.startCrawler(1))
        # 관심차량 찜 중지.
        self.q_favorite_stop_button.clicked.connect(self.stopCrawling)

        # 찜 종료 정보 수집.
        # 찜 종료 정보 수집 시작.
        self.q_favorite_ended_start_button.clicked.connect(
            lambda: self.startCrawler(2))
        # 찜 종료 정보 수집 중지.
        self.q_favorite_ended_stop_button.clicked.connect(self.stopCrawling)

        # 내입찰 완료 정보 수집.
        # 내입찰 완료 정보 수집 시작.
        self.q_auction_ended_start_button.clicked.connect(
            lambda: self.startCrawler(3))
        # 내입찰 완료 정보 수집 중지.
        self.q_auction_ended_stop_button.clicked.connect(self.stopCrawling)

        # 찜 차량 입찰.
        self.q_auction_start_button.clicked.connect(lambda: self.startCrawler(4)) # 찜 차량 입찰 시작.
        self.q_auction_stop_button.clicked.connect(self.auctionStop) # 찜 차량 입찰 중지.

        # url
        self.q_url.textChanged.connect(self.setUrl)  # url 주소.
        # url 검색.
        self.q_url_button.clicked.connect(lambda: self.startCrawler(0))

        # 스크롤 제한 여부.
        self.is_limit_scroll = self.q_limit_scroll.isChecked()
        self.q_limit_scroll.stateChanged.connect(self.setScrollChange)

        # 스크롤 제한 갯수.
        self.limit_scroll_count = self.q_limit_scroll_count.value()
        self.q_limit_scroll_count.valueChanged.connect(self.setScrollCount)

        # 크롤링 시작 인덱스.
        self.crawling_start_index = self.q_crawling_start_index.value()
        self.q_crawling_start_index.valueChanged.connect(self.setCrawlingStartIndex)

        # 스크롤 대기 시간.
        self.wait_scroll_time = self.q_wait_scroll_time.value()
        self.q_wait_scroll_time.valueChanged.connect(self.setWaitScrollTime)

    @pyqtSlot(int, int)
    def setProgressBar(self, target, value):

        if target == 1:  # 관심차량 찜.
            self.q_favorite_progressbar.setValue(value)
        elif target == 2:  # 찜 종료 정보 수집.
            self.q_favorite_ended_progressbar.setValue(value)
        elif target == 3:  # 내입찰 완료 정보 수집.
            self.q_auction_ended_progressbar.setValue(value)
        elif target == 4:  # 찜 차량 입찰.
            self.q_auction_progressbar.setValue(value)
        else:
            pass

    @pyqtSlot(int, bool)
    def setSingleExecution(self, target, is_working):
        if self.is_full_process:
            return

        self.q_process_start_button.setEnabled(not is_working)
        self.q_process_stop_button.setEnabled(not is_working)

        for i in range(5):

            enabled_value = target == i if is_working else True

            if (i == 0):
                self.q_url_group.setEnabled(not is_working)
            elif (i == 1):
                self.q_favorite_group.setEnabled(enabled_value)
                self.q_favorite_enable_check.setEnabled(not is_working)
                self.q_favorite_start_button.setEnabled(not is_working)
                self.q_favorite_stop_button.setEnabled(is_working)
            elif (i == 2):
                self.q_favorite_ended_group.setEnabled(enabled_value)
                self.q_favorite_ended_enable_check.setEnabled(not is_working)
                self.q_favorite_ended_start_button.setEnabled(not is_working)
                self.q_favorite_ended_stop_button.setEnabled(is_working)
            elif (i == 3):
                self.q_auction_ended_group.setEnabled(enabled_value)
                self.q_auction_ended_enable_check.setEnabled(not is_working)
                self.q_auction_ended_start_button.setEnabled(not is_working)
                self.q_auction_ended_stop_button.setEnabled(is_working)
            elif (i == 4):
                self.q_auction_group.setEnabled(enabled_value)
                self.q_auction_enable_check.setEnabled(not is_working)
                self.q_auction_start_button.setEnabled(not is_working)
                self.q_auction_stop_button.setEnabled(is_working)

    

    @pyqtSlot(str)
    def statusShowMessage(self, message):
        self.statusBar().showMessage('{}'.format(message))

    """ 프로세스 """

    pyqtSlot(str)
    def setProcessLabelText(self, text):
        self.q_process_label.setText('{}'.format(text))

    def startProcess(self):
        self.is_full_process = True

        self.setProcess(True)
        self.process_worker = Process(self)
        self.process_worker.start()

    def stopProcess(self):
        if self.is_full_process == False:
            return

        self.stopCrawling()
        self.process_worker.stop()

    def setProcess(self, is_working):
        if self.is_full_process == False:
            return
        for i in range(5):

            if is_working:
                self.q_favorite_group.setEnabled(
                    self.q_favorite_enable_check.isChecked())
                self.q_favorite_ended_group.setEnabled(
                    self.q_favorite_ended_enable_check.isChecked())
                self.q_auction_ended_group.setEnabled(
                    self.q_auction_ended_enable_check.isChecked())
                self.q_auction_group.setEnabled(
                    self.q_auction_enable_check.isChecked())
            else:
                self.q_favorite_group.setEnabled(True)
                self.q_favorite_ended_group.setEnabled(True)
                self.q_auction_ended_group.setEnabled(True)
                self.q_auction_group.setEnabled(True)

            self.q_process_start_button.setEnabled(not is_working)
            self.q_process_stop_button.setEnabled(is_working)

            self.q_favorite_enable_check.setEnabled(not is_working)
            self.q_favorite_start_button.setEnabled(not is_working)
            self.q_favorite_stop_button.setEnabled(not is_working)

            self.q_favorite_ended_enable_check.setEnabled(not is_working)
            self.q_favorite_ended_start_button.setEnabled(not is_working)
            self.q_favorite_ended_stop_button.setEnabled(not is_working)

            self.q_auction_ended_enable_check.setEnabled(not is_working)
            self.q_auction_ended_start_button.setEnabled(not is_working)
            self.q_auction_ended_stop_button.setEnabled(not is_working)

            self.q_auction_enable_check.setEnabled(not is_working)
            self.q_auction_start_button.setEnabled(not is_working)
            self.q_auction_stop_button.setEnabled(not is_working)

            self.q_url_group.setEnabled(not is_working)

    """ 관심차량 찜 """

    @pyqtSlot(int)
    def finishedThread(self, crawling_type):
        if crawling_type == 1:
            self.finished_favorite_signal.emit()
        elif crawling_type == 2:
            self.finished_favorite_ended_signal.emit()
        elif crawling_type == 3:
            self.finished_auction_ended_signal.emit()

    def startCrawler(self, crawling_type):
        self.setProgressBar(crawling_type, 0)

        self.crawler = Crawler(self.parent, self, crawling_type)

        if crawling_type == 4:
            self.finished_input_estimate_signal.connect(self.crawler.setWaitCalculator)

        self.crawler.start()

    def stopCrawling(self):
        if self.crawler == None:
            return

        if self.crawler.isRunning:
            self.crawler.stop()

    # 4.입찰 정지 버튼.
    def auctionStop(self):
        self.stopCrawling()

    def setUrl(self):
        self.car_url = self.q_url.text()

    def setScrollChange(self):
        self.is_limit_scroll = self.q_limit_scroll.isChecked()

    def setScrollCount(self):
        self.limit_scroll_count = self.q_limit_scroll_count.value()

    def setCrawlingStartIndex(self):
        self.crawling_start_index = self.q_crawling_start_index.value()

    def setWaitScrollTime(self):
        self.wait_scroll_time = self.q_wait_scroll_time.value()

    """ 찜목록 입찰 """

    @pyqtSlot()
    def startEstimateHeydealerDB(self):
        self.estimate_calculator = EstimateCalculator(self.parent, self, None)
        self.estimate_calculator.start()

    @pyqtSlot(str)
    def inputEstimatePrice(self, text):
        self.input_estimate = InputEstimate(self, text)
        self.input_estimate.start()

    @pyqtSlot() # inputEstimate 쓰레드로부터 시그널을 받는다.
    def finishedInputEstimatePriceCrawling(self):
        self.finished_input_estimate_signal.emit(False) # 크롤러 쓰레드로 보낸다.

    def closeGUI(self):
        self.stopCrawling()
        self.driver.quit()

    def closeEvent(self, event):
        self.closeGUI()
        event.accept()

    
