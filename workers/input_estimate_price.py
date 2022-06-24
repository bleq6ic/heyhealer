from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class InputEstimate(QThread, QObject):

    finished_input_signal = pyqtSignal()

    def __init__(self, heyhealer_parent, text):
        super().__init__()
        self.heyhealer_parent = heyhealer_parent
        self.text = text
        self.driver = self.heyhealer_parent.driver

        self.finished_input_signal.connect(self.heyhealer_parent.finishedInputEstimatePriceCrawling)

    def run(self):
        driver = self.driver
        url = self.heyhealer_parent.curr_car_data['url']
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)

        try:
            textarea = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//textarea[@class="css-1uoj5n4"]')))
            textarea.send_keys(Keys.CONTROL + "a");
            textarea.send_keys(Keys.DELETE);
            textarea.clear()
            textarea.send_keys(self.text)
            textarea.send_keys(Keys.TAB)
            sleep(1)
        except:
            pass

        self.finished_input_signal.emit()

