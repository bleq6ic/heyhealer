from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class HeyhealerLoginThread(QThread):
    
    login_status_signal = pyqtSignal(int)

    def __init__(self, parent, qWidget):
        super().__init__(parent)
        self.parent = parent
        self.qwidget = qWidget
        self.users_data = self.parent.pd_users_data


    def run(self):
        # 시그널 연결.
        self.login_status_signal.connect(self.parent.setMyApp) # main > MyApp
        self.login_status_signal.connect(self.qwidget.heyhealerLoginStatus) # HeyHealerLoginGUI

        login_status = 0  # 0:아이디없음, 1:아이디 존재, 비밀번호 불일치, 2: 정상로그인
        for i in self.users_data.index:
            login_status = 0

            if self.users_data['id'][i] == self.qwidget.heyhealer_id:
                login_status += 1

                if self.users_data['pw'][i] == self.qwidget.heyhealer_pw:
                    login_status += 1
                    self.user_index = i
                    user_data = self.users_data.loc[i]
                    self.parent.pd_user_data = user_data
                    break
        
        self.login_status_signal.emit(login_status) # 시그널



