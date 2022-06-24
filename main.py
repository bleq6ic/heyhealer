import sys
import pandas as pd
import json
from workers.databaser import MySQL
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *  
from PyQt5 import uic

from time import sleep

from gui.heydealer_login_gui import HeydealerLoginGUI
from gui.heyhealer_login_gui import HeyHealerLoginGUI
from gui.heyhealer import HeyHealer


form_class = uic.loadUiType("designer/main.ui")[0]

class MyApp(QMainWindow, form_class):

    #signal.
    heyhealer_all_close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.heyhealer_login_status = 0 # heyhealer 로그인 상태.
        self.pd_user_data = None # from workers.healer_loger.
        self.driver = None

        # 데이터를 불러온다
        self.pd_users_data = pd.DataFrame(MySQL().selectFromTable("users"))
        self.pd_categories = pd.DataFrame(MySQL().selectFromTable("categories"))
        self.pd_match_accident_repairs = jsonHeydealerAccidentRepairs()  # 성능기록부 정보. (기본베이스)

        self.setUi()

        # 최초 1회 실행.
        self.setMyApp(self.heyhealer_login_status)
        self.clickHeyhealerLoginoutButton()


    def setUi(self):
        self.statusBarShowMessage("Hey! Healer!")

        self.q_heyhealer_loginout_button.clicked.connect(
            self.clickHeyhealerLoginoutButton)
        self.q_heydealer_login_button.clicked.connect(self.heydealerLoginButton)

    @pyqtSlot(int)
    def setMyApp(self, status):
        self.heyhealer_login_status = status
        if self.heyhealer_login_status != 2:
            self.q_user_name.setText("로그인이 되어있지 않습니다")
            self.q_login_text.setText("로그인을 하셔야 정상적인 사용이 가능합니다")
            self.q_heyhealer_loginout_button.setText("로그인")
        else:
            self.q_user_name.setText(self.pd_user_data['name'] + " 님,")
            self.q_login_text.setText("Hey! Helaer 에 오신걸 환영합니다")
            self.q_heyhealer_loginout_button.setText("로그아웃")

        self.q_user_buttons.setEnabled(self.heyhealer_login_status == 2)

    def clickHeyhealerLoginoutButton(self):
        if self.heyhealer_login_status != 2: # 로그인 버튼
            self.q_heyhealer_loginout_widget.setEnabled(False)
            login_window = HeyHealerLoginGUI(self)
            login_window.show()
            login_window.exec()
            self.q_heyhealer_loginout_widget.setEnabled(True)
        else: # 로그아웃 버튼   
            self.setMyApp(0)

    def heydealerLoginButton(self):
        self.q_heydealer_login_button.setEnabled(False)
        self.heydealer_worker = HeydealerLoginGUI(self)
        self.heydealer_worker.show()
        self.heydealer_worker.exec()
        self.q_heydealer_login_button.setEnabled(True)

    @pyqtSlot(str)
    def newHeyhealer(self, heydealer_id):

        x = HeyHealer(self, self.driver, heydealer_id)
        sleep(1)
        x.show()

    @pyqtSlot(str, str)
    def showMessageBox(self, title, text):
        QMessageBox.about(self, '{}'.format(title), '{}'.format(text))

    @pyqtSlot(str)
    def statusBarShowMessage(self, message):
        self.statusBar().showMessage('{}'.format(message))

def jsonHeydealerAccidentRepairs():
    with open('accident_repairs.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    accident_repairs = json_data['accident_repairs']
    return pd.DataFrame(accident_repairs)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()
