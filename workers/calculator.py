import enum
from math import ceil, floor
import json
from numpy import void
import pandas as pd

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from IPython.display import display

from workers.databaser import MySQL


class EstimateCalculators(QObject):


    # ver3 (데이터베이스 활용)

    def hhCalculatorVer1(self, curr_car_data, data_list):

        if len(data_list) == 0:
            return 0

        # 수입차, 국산차 구분.
        is_imported = self.isImported(curr_car_data)

        config_path = 'healer_config.json'
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        outside_down_price = config_data['Deduct']['imported'][
            'outside'] if is_imported else config_data['Deduct']['domestic']['outside']
        wheel_down_price = config_data['Deduct']['imported'][
            'wheel'] if is_imported else config_data['Deduct']['domestic']['wheel']
        tire_down_price = config_data['Deduct']['imported']['tire'] if is_imported else config_data['Deduct']['domestic']['tire']
        spairkey_down_price = config_data['Deduct']['imported'][
            'spairkey'] if is_imported else config_data['Deduct']['domestic']['spairkey']

        color_db = MySQL().selectWhereColumn('colors', 'detail_color', curr_car_data['detail_color'])
        if len(color_db) > 0:
            curr_car_data['color'] = color_db[0]
        
        for i, v in enumerate(data_list):

            # 선택가 목록, 최고가 목록 분류.
            # 공통 가격 표시.
            v['auction_price'] = v['selective_price'] if v['selective_price'] != 0 else v['max_price']

            # 역 감가. 차량 가격 측정은 감가 요인을 감안한 옥션가.
            r_outside = v['scratch_outside'] * outside_down_price
            r_wheel = v['scratch_wheel'] * wheel_down_price
            r_tire = v['tire_count'] * tire_down_price

            if v['key_count'] < 2:
                r_key_count = spairkey_down_price
            else:
                r_key_count = 0
            

            total_deduct = r_outside + r_wheel + r_tire + r_key_count
            origin_price = v['auction_price']
            v['auction_price_with_deduct'] = origin_price + total_deduct

            # 차량 등급(조건) 포인트 설정.

            if curr_car_data['color'] == "검정":
                my_color_level = 2.0
            elif curr_car_data['color'] == "흰색":
                my_color_level = 2.0
            elif curr_car_data['color'] == "회색":
                my_color_level = 1.0
            elif curr_car_data['color'] == "미색":
                my_color_level = 1.0
            else:
                my_color_level = 0.0
            
            if v['color'] == "검정":
                data_color_level = 2.0
            elif v['color'] == "흰색":
                data_color_level = 2.0
            elif v['color'] == "회색":
                data_color_level = 1.0
            elif v['color'] == "미색":
                data_color_level = 1.0
            else:
                data_color_level = 0.0

            if curr_car_data['accident'] == "완전무사고":
                my_acc_level = 4.0
            elif curr_car_data['accident'] == "단순교환":
                my_acc_level = 2.0
            else:
                my_acc_level = 0.0

            if v['accident'] == "완전무사고":
                data_acc_level = 4.0
            elif v['accident'] == "단순교환":
                data_acc_level = 2.0
            else:
                data_acc_level = 0.0

            years_level_score = (v['years'] - curr_car_data['years']) * 1.5
            accident_level_score = data_acc_level - my_acc_level
            color_level_score = data_color_level - my_color_level
            mileage_level_score = (curr_car_data['mileage'] - v['mileage']) * 0.0001
            
            level_score = color_level_score + mileage_level_score + accident_level_score + years_level_score
            
            v['level_score'] = round(level_score, 1)

        df_data_list = pd.DataFrame(data_list)
        
        # 낮은 가격 순으로 정렬.
        df_data_list = df_data_list.sort_values('auction_price_with_deduct')
        data_list = df_data_list.to_dict('records')

        new_data_list = []
        for i, v in enumerate(data_list):
            if v['level_score'] > 2.5 or v['level_score'] <= -1.5:
                continue
            new_data_list.append(data_list[i])
        
        if len(new_data_list) > 0:
            return new_data_list[0]['auction_price_with_deduct']
        else:
            return 0
     

    def hdCalcualtorVer1(self, car_data, data_list):
        color_db = MySQL().selectWhereColumn('colors', 'detail_color', car_data['detail_color'])
        if len(color_db) > 0:
            car_data['color'] = color_db[0]['normal_color']
        

    # ver2
    def hdCalculatorVer2(self, car_data, data_list):

        if len(data_list) < 1:
            return 0

        # 수입차/국산차 구분.
        is_imported = self.isImported(car_data)

        color_db = MySQL().selectWhereColumn('colors', 'detail_color', car_data['detail_color'])
        if len(color_db) > 0:
            car_data['color'] = color_db[0]['normal_color']
        
        for i, v in enumerate(data_list):

            # 차량 등급(조건) 포인트 설정.

            if car_data['color'] == "검정":
                my_color_level = 2.0
            elif car_data['color'] == "흰색":
                my_color_level = 2.0
            elif car_data['color'] == "회색":
                my_color_level = 1.0
            elif car_data['color'] == "미색":
                my_color_level = 1.0
            else:
                my_color_level = 0.0
            
            if v['color'] == "검정":
                data_color_level = 2.0
            elif v['color'] == "흰색":
                data_color_level = 2.0
            elif v['color'] == "회색":
                data_color_level = 1.0
            elif v['color'] == "미색":
                data_color_level = 1.0
            else:
                data_color_level = 0.0

            if car_data['accident'] == "완전무사고":
                my_acc_level = 4.0
            elif car_data['accident'] == "단순교환":
                my_acc_level = 2.0
            else:
                my_acc_level = 0.0

            if v['accident'] == "완전무사고":
                data_acc_level = 4.0
            elif v['accident'] == "단순교환":
                data_acc_level = 2.0
            else:
                data_acc_level = 0.0

            years_level_score = (v['years'] - car_data['years']) * 1.5
            color_level_score = data_color_level - my_color_level
            accident_level_score = data_acc_level - my_acc_level
            mileage_level_score = (car_data['mileage'] - v['mileage']) * 0.0001
            
            level_score = color_level_score + mileage_level_score + accident_level_score + years_level_score
            
            v['level_score'] = round(level_score, 1)

        df_data_list = pd.DataFrame(data_list)
        
        # 낮은 가격 순으로 정렬.
        if len(df_data_list) > 1:
            df_data_list = df_data_list.sort_values('max_price')
        data_list = df_data_list.to_dict('records')

        new_data_list = []
        for i, v in enumerate(data_list):
            if v['level_score'] > 2.5 or v['level_score'] <= -1.5:
                continue
            new_data_list.append(data_list[i])
        
        if len(new_data_list) > 0:
            return new_data_list[0]['max_price']
        else:
            return 0


    def isImported(self, car_data):
        # 수입차/국산차 구분.
        domestic_brands = ['현대', '제네시스', '기아', '쉐보레(GM대우)', '르노삼성', '쌍용', ]
        is_imported = True
        for d_brand in domestic_brands:
            if d_brand == car_data['brand']:
                is_imported = False
                break

        return is_imported
