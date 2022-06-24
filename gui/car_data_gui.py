from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

from workers.estimate_calculator import EstimateCalculator

form_class = uic.loadUiType("designer/car_data.ui")[0]


class CarDataGUI(QWidget, form_class):
    
    close_signal = pyqtSignal()

    def __init__(self, parent, heyhealer_parent):
        super().__init__()
        self.parent = parent
        self.heyhealer_parent = heyhealer_parent
        self.setupUi(self)
        self.setUi()
        self.show()

    def setUi(self):
        self.q_auction_play.setVisible(True)
        self.q_auction_end.setVisible(False)

        self.q_auction_calculator_button.clicked.connect(self.clickAuctionCalculatorButton)

        self.setEnabledAuctionCalculatorButton(False)

    def closeEvent(self, QCloseEvent):
        self.close_signal.emit()
        self.deleteLater()
        QCloseEvent.accept()

    @pyqtSlot(str, str)
    def showMessageBox(self, title, text):
        QMessageBox.about(self, '{}'.format(title), '{}'.format(text))

    @pyqtSlot(str)
    def windowTitle(self, title):
        self.setWindowTitle('{}'.format(title))

    @pyqtSlot(str, str, str, str, str, int, int, int, int, str, str, str, str, str, str, str, int)
    def setTextCarData(self, car_number, brand, model, model_detail, grade, years, month, car_years, mileage, color, color_detail, fuel, mission, seat, lease, region, car_new_price):
        self.q_car_number.setText('{}'.format(car_number))
        self.q_brand.setText('{}'.format(brand))
        self.q_model.setText('{}'.format(model))
        self.q_model_detail.setText('{}'.format(model_detail))
        self.q_grade.setText('{}'.format(grade))
        self.q_years.setText('{}'.format(years))
        self.q_month.setText('{}'.format(month))
        self.q_car_years.setText('{}'.format(car_years))
        comma_mileage = format(mileage, ',')
        self.q_mileage.setText('{}'.format(comma_mileage))
        self.q_color.setText('{}'.format(color))
        self.q_color_detail.setText('{}'.format(color_detail))
        seat_text = "정보없음" if seat == "null" else seat
        self.q_seat.setText('{}'.format(seat_text))
        self.q_region.setText('{}'.format(region))
        self.q_fuel.setText('{}'.format(fuel))
        self.q_mission.setText('{}'.format(mission))
        self.q_lease.setText('{}'.format(lease))
        car_new_price_text = "정보없음" if car_new_price == 0 else str(
            format(car_new_price, ',')) + " 만원"
        self.q_car_new_price.setText('{}'.format(car_new_price_text))

    @pyqtSlot(int, int, int, str, int, int)
    def setTextDeductData(self, scratch_outside, scratch_wheel, tire, tire_detail, key_count, special_key_index):
        color_red = 'Color : red'
        color_black = 'Color : black'

        self.q_outside.setText('{}'.format(scratch_outside))
        outside_color = color_red if scratch_outside > 0 else color_black
        self.q_outside.setStyleSheet(outside_color)

        self.q_wheel.setText('{}'.format(scratch_wheel))
        wheel_color = color_red if scratch_wheel > 0 else color_black
        self.q_wheel.setStyleSheet(wheel_color)

        self.q_tire.setText('{}'.format(tire))
        self.q_tire_detail.setText('{}'.format(tire_detail))
        tire_color = color_red if tire > 0 else color_black
        self.q_tire.setStyleSheet(tire_color)
        self.q_tire_detail.setStyleSheet(tire_color)

        self.q_key_count.setText('{}'.format(key_count))
        key_color = color_red if key_count < 2 else color_black
        self.q_key_count.setStyleSheet(key_color)

        special_key_text = "적용안됨" if special_key_index == 0 else "없음" if special_key_index == 1 else "있음"
        special_key_color = color_red if special_key_text == "없음" else color_black
        self.q_special_key.setText(special_key_text)
        self.q_special_key.setStyleSheet(special_key_color)

    @pyqtSlot(int, str)  # int = 0: setText, 1: append, 2:clear
    def setTextBrowserOptionData(self, index, option):
        if index == 0:
            self.q_options.setText('{}'.format(option))
        elif index == 1:
            self.q_options.append('{}'.format(option))
        else:
            self.q_options.clear()

    @pyqtSlot(int, str)# int = 0: setText, 1: append, 2:clear
    def setTextBrowserAddOptionData(self, index, add_option):
        if index == 0:
            self.q_add_options.setText('{}'.format(add_option))
        elif index == 1:
            self.q_add_options.append('{}'.format(add_option))
        else:
            self.q_add_options.clear()

    @pyqtSlot(int, str)  # int = 0: setText, 1: append, 2:clear
    def setTextBrowserNewReleaseData(self, index, new_release):
        relaese_text = "출고 정보가 없습니다" if new_release == "null" else new_release

        if index == 0:
            self.q_new_release.setText('{}'.format(relaese_text))
        elif index == 1:
            self.q_new_release.append('{}'.format(relaese_text))
        else:
            self.q_new_release.clear()

    @pyqtSlot(str, str)
    def setTextAccidentData(self, acc_writer, acc):
        color_red = 'Color : red'
        color_black = 'Color : black'

        self.q_accident_writer.setText('{}'.format(acc_writer))
        accident_color = color_red if acc == "유사고" else color_black
        self.q_accident.setText('{}'.format(acc))
        self.q_accident.setStyleSheet(accident_color)

    @pyqtSlot(str)
    def appendPaintData(self, paint):
        self.q_accident_repairs_paint.append('{}'.format(paint))

    @pyqtSlot(str)
    def appendSheetMetalData(self, sheet_metal):
        self.q_accident_repairs_sheet_metal.append('{}'.format(sheet_metal))

    @pyqtSlot(str)
    def appendChangedData(self, changed):
        self.q_accident_repairs_changed.append('{}'.format(changed))

    @pyqtSlot(int, int, int)
    def setTextAccidentRepairsCountData(self, paint_count, sheet_metal_count, changed_count):
        self.q_accident_repairs_paint_count.setText(
            '도색 : (' + '{}'.format(paint_count) + ')')
        self.q_accident_repairs_sheet_metal_count.setText(
            '판금 : (''{}'.format(sheet_metal_count) + ')')
        self.q_accident_repairs_changed_count.setText(
            '교환 : (''{}'.format(changed_count) + ')')

    @pyqtSlot(str, str, int, int, int, str)
    def setTextAccidentHistory(self, usage_history, flooding_loss, my_car_damage, another_blow, change_owner, acc_history):
        color_red = 'Color : red'
        color_black = 'Color : black'

        usage_history_color = color_red if usage_history != "없음" else color_black
        self.q_usage_history.setText('{}'.format(usage_history))
        self.q_usage_history.setStyleSheet(usage_history_color)

        flooding_loss_color = color_red if flooding_loss != "없음" else color_black
        self.q_flooding_loss.setText('{}'.format(flooding_loss))
        self.q_flooding_loss.setStyleSheet(flooding_loss_color)

        my_car_damage_color = color_red if my_car_damage >= 300 else color_black
        self.q_my_car_damage.setText('{}'.format(my_car_damage))
        self.q_my_car_damage.setStyleSheet(my_car_damage_color)

        self.q_another_blow.setText('{}'.format(another_blow))
        self.q_change_owner.setText('{}'.format(change_owner))
        self.q_acc_history.setText('{}'.format(acc_history))

    @pyqtSlot(str)
    def setTextComments(self, comments):
        self.q_comments.setText('{}'.format(comments))

    @pyqtSlot(str)
    def setTextHeydealerComment(self, heydealer_comment):
        self.q_heydealer_comment.setText('{}'.format(heydealer_comment))

    @pyqtSlot(str, int, str, int, int, int, int, int)
    def setTextAuction(self, auction, current_bidder, left_time, bidder, end_date, selective_price, max_price, my_price):
        if auction == "경매종료" or auction == "유효기간만료":
            self.q_auction_play.setVisible(False)
            self.q_auction_end.setVisible(True)
            self.q_auction_end.setTitle('{}'.format(auction))
            self.q_bidder.setText('{}'.format(bidder))
            end_date_text = "정보없음" if end_date == -1 else str(end_date)
            self.q_auction_end_date.setText('{}'.format(end_date_text))
            selective_price_text = "정보없음" if selective_price == 0 else str(
                format(selective_price, ',')) + " 만원"
            self.q_selective_price.setText('{}'.format(selective_price_text))
            max_price_text = "정보없음" if max_price == 0 else str(
                format(max_price, ',')) + " 만원"
            self.q_max_price.setText('{}'.format(max_price_text))
            my_price_text = "정보없음" if my_price == 0 else str(
                format(my_price, ',')) + " 만원"
            self.q_my_price.setText('{}'.format(my_price_text))
        else:
            self.q_auction_end.setVisible(False)
            self.q_auction_play.setVisible(True)
            self.q_auction_play.setTitle('{}'.format(auction))
            self.q_current_bidder.setText('{}'.format(current_bidder))
            self.q_left_time.setText('{}'.format(left_time))

    @pyqtSlot(bool)
    def setEnabledAuctionCalculatorButton(self, value):
        self.q_auction_calculator_button.setEnabled(value)

    @pyqtSlot(int)
    def setEstimatePrice(self, price):

        if price == 0:
            text = "데이터 부족"
        else:
            text = str(format(price, ',')) + " 만원"

        self.q_estimate_price.setText(text)
        self.setEnabledAuctionCalculatorButton(True)

    def clickAuctionCalculatorButton(self):
        self.calculator = EstimateCalculator(self.parent, self.heyhealer_parent, self)
        self.calculator.start()
        self.setEnabledAuctionCalculatorButton(False)

