from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pymysql
import pandas as pd
import json
from workers.heyhealer_login_thread import HeyhealerLoginThread

heyhealer_login_form = uic.loadUiType("designer/heyhealer_login.ui")[0]

class HeyHealerLoginGUI(QDialog, QWidget, heyhealer_login_form):

    close_signal = pyqtSignal(int) # hey healer 로그인창 종료 시그널. 종료 타입 int

    config_path = "healer_config.json"

    heyhealer_id = ""
    heyhealer_pw = ""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.config_file = self.ConfigFile()
        self.setupUi(self)
        self.setUi()

    def ConfigFile(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def setUi(self):
        if self.config_file['HeyHealer']['autosave'] != self.q_auto_save.isChecked():
            self.q_auto_save.toggle()

        if self.config_file['HeyHealer']['autosave']:
            id_text = self.config_file['HeyHealer']['id']
            self.q_heyhealer_id.setText(id_text)
            self.heyhealer_id = self.q_heyhealer_id.text()

        self.q_heyhealer_id.textChanged.connect(self.inputHeyhealerId)
        self.q_heyhealer_pw.textChanged.connect(self.inputHeyhealerPw)
        self.q_heyhealer_pw.returnPressed.connect(
            self.clickLoginButton)
        self.q_heyhealer_login_button.clicked.connect(
            self.clickLoginButton)


    def clickLoginButton(self):

        if self.heyhealer_id == "":
            self.showMessageBox("아이디를 입력해주세요")
            return

        if self.heyhealer_pw == "":
            self.showMessageBox("비밀번호를 입력해주세요")
            return

        self.q_heyhealer_login_widget.setEnabled(False)
        self.showMessageBox("Hey! Healer 로그인 중입니다..")

        x = HeyhealerLoginThread(self.parent, self)
        x.start()

    def inputHeyhealerId(self):
        self.heyhealer_id = self.q_heyhealer_id.text()

    def inputHeyhealerPw(self):
        self.heyhealer_pw = self.q_heyhealer_pw.text()

    @pyqtSlot(int)  # 0:아이디없음, 1:아이디 존재, 비밀번호 불일치, 2: 정상로그인
    def heyhealerLoginStatus(self, status):
        if status == 0:
            self.q_heyhealer_login_widget.setEnabled(True)
            self.showMessageBox("존재하는 아이디가 없습니다")
        elif status == 1:
            self.q_heyhealer_login_widget.setEnabled(True)
            self.showMessageBox("비밀번호가 일치하지 않습니다")
        elif status == 2:
            if self.q_auto_save.isChecked():
                self.setConfig()

            self.close()

    def showMessageBox(self, text):
        self.q_heyhealer_status.setText(text)

    def setConfig(self):
        self.config_file['HeyHealer']['autosave'] = True
        self.config_file['HeyHealer']['id'] = self.heyhealer_id

        with open(self.config_path, 'w') as outfile:
            json.dump(self.config_file, outfile)