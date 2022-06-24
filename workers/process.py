
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os

from bs4 import BeautifulSoup


class Process(QThread):

    label_signal_to_widget = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.is_processing = True
        self.is_finished_favorite = False
        self.is_finished_favorite_ended = False
        self.is_finished_auction_ended = False

        # 시그널 연결.
        self.parent.finished_favorite_signal.connect(self.finishedFavorite)
        self.parent.finished_favorite_ended_signal.connect(
            self.finishedFavoriteEnded)
        self.parent.finished_auction_ended_signal.connect(
            self.finishedAuctionEnded)

        self.label_signal_to_widget.connect(self.parent.setProcessLabelText)

    def run(self):
        favorite_checked = self.parent.q_favorite_enable_check.isChecked()
        favorite_ended_checked = self.parent.q_favorite_ended_enable_check.isChecked()
        auction_ended_checked = self.parent.q_auction_ended_enable_check.isChecked()
        auction_checked = self.parent.q_auction_enable_check.isChecked()

        start_time = time.time()

        run_index = 0
        while self.is_processing:
            run_index += 1
            if favorite_checked:

                if self.is_processing == False:
                    break

                self.label_signal_to_widget.emit("관심차량 프로세스 진행 중")

                self.parent.startCrawler(1)

                while self.is_finished_favorite == False:
                    if self.is_processing == False:
                        break
                    time.sleep(1)

            if favorite_ended_checked:

                if self.is_processing == False:
                    break

                self.label_signal_to_widget.emit("찜 종료 프로세스 진행 중")

                self.parent.startCrawler(2)

                while self.is_finished_favorite_ended == False:
                    if self.is_processing == False:
                        break
                    time.sleep(1)

            if auction_ended_checked:

                if self.is_processing == False:
                    break

                self.label_signal_to_widget.emit("내입찰 완료 프로세스 진행 중")

                self.parent.startCrawler(3)

                while self.is_finished_auction_ended == False:
                    if self.is_processing == False:
                        break
                    time.sleep(1)

            if run_index > 2:
                break

        total_time = time.time() - start_time
        self.parent.statusShowMessage(
            "프로세스 종료 : 소요시간 " + str(round(total_time, 1)) + "초")

        self.label_signal_to_widget.emit("선택된 프로세스를")
        self.parent.setProcess(False)
        self.parent.is_full_process = False

    @pyqtSlot()
    def finishedFavorite(self):
        self.is_finished_favorite = True

    @pyqtSlot()
    def finishedFavoriteEnded(self):
        self.is_finished_favorite_ended = True

    @pyqtSlot()
    def finishedAuctionEnded(self):
        self.is_finished_auction_ended = True

    def stop(self):
        self.is_processing = False
        self.quit()
        self.wait(3000)
