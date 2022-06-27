# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\grdver\Documents\Python Projects\heyhealer\designer\search_heydealer.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(555, 376)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 470, 340))
        self.groupBox.setObjectName("groupBox")
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 30, 450, 71))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(80, 30, 40, 22))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(210, 30, 40, 22))
        self.label_3.setObjectName("label_3")
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox.setGeometry(QtCore.QRect(10, 30, 62, 22))
        self.doubleSpinBox.setDecimals(1)
        self.doubleSpinBox.setMinimum(-20.0)
        self.doubleSpinBox.setMaximum(0.0)
        self.doubleSpinBox.setProperty("value", -2.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_2.setGeometry(QtCore.QRect(140, 30, 62, 22))
        self.doubleSpinBox_2.setDecimals(1)
        self.doubleSpinBox_2.setMaximum(20.0)
        self.doubleSpinBox_2.setProperty("value", 2.0)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(120, 30, 10, 22))
        self.label.setObjectName("label")
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 110, 450, 71))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(130, 30, 191, 22))
        self.label_4.setObjectName("label_4")
        self.spinBox = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBox.setGeometry(QtCore.QRect(80, 30, 42, 22))
        self.spinBox.setProperty("value", 5)
        self.spinBox.setObjectName("spinBox")
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setGeometry(QtCore.QRect(10, 30, 71, 22))
        self.label_5.setObjectName("label_5")
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 190, 450, 80))
        self.groupBox_4.setObjectName("groupBox_4")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox.setGeometry(QtCore.QRect(10, 30, 420, 22))
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox_2.setGeometry(QtCore.QRect(10, 50, 420, 22))
        self.checkBox_2.setChecked(True)
        self.checkBox_2.setObjectName("checkBox_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "매입시세 조회 필터"))
        self.groupBox_2.setTitle(_translate("Form", "주행거리 검색 범위"))
        self.label_2.setText(_translate("Form", "만 km "))
        self.label_3.setText(_translate("Form", "만 km"))
        self.label.setText(_translate("Form", "~"))
        self.groupBox_3.setTitle(_translate("Form", "입찰자 수"))
        self.label_4.setText(_translate("Form", "명 미만이라면 검색하지 않습니다"))
        self.label_5.setText(_translate("Form", "입찰자 수가"))
        self.groupBox_4.setTitle(_translate("Form", "사고유무"))
        self.checkBox.setText(_translate("Form", "검색 차량 매물이 \'완전무사고\'라면 \'단순교환\' 차량을 검색하지 않습니다"))
        self.checkBox_2.setText(_translate("Form", "\'유사고\' 차량을 검색하지 않습니다"))

