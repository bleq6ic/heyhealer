from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from workers.heydealer_login_thread import HeydealerLoginThread
from selenium import webdriver

form_class = uic.loadUiType("designer/heydealer_login.ui")[0]

class HeydealerLoginGUI(QDialog, form_class):

    heydealer_id = ""
    heydealer_pw = ""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.setUi()

        self.driver = None

    def setUi(self):

        self.q_heydealer_id.textChanged.connect(self.setHeydealerId)
        self.q_heydealer_pw.textChanged.connect(self.setHeydealerPw)
        self.q_heydealer_pw.returnPressed.connect(
            self.clickHeydealerLoginButton)
        self.q_heydealer_login_button.clicked.connect(
            self.clickHeydealerLoginButton)

    def setHeydealerId(self):
        self.heydealer_id = self.q_heydealer_id.text()

    def setHeydealerPw(self):
        self.heydealer_pw = self.q_heydealer_pw.text()

    def clickHeydealerLoginButton(self):

        self.q_heydealer_login_group.setEnabled(False)

        self.login_thread = HeydealerLoginThread(self.parent, self, self.heydealer_id, self.heydealer_pw, self.q_headless_check.isChecked())
        self.login_thread.start()

    @pyqtSlot(str)
    def setStatusMessage(self, text):
        self.q_status.setText(text)

        if text == "로그인에 성공하였습니다":
            self.close()
            
        elif text == "로그인에 실패하였습니다":
            self.q_heydealer_login_group.setEnabled(True)


