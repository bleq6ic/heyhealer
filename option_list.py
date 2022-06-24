import pymysql
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import re
import pandas as pd
from pandas import DataFrame
from IPython.display import display
import sqlalchemy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from time import sleep
import time
import json

from workers.databaser import MySQL

from bs4 import BeautifulSoup

class EditOption():
    def __init__(self):
        self.add_option_list()

    def add_option_list(self):
        car_list = MySQL().selectFromTable('heydealer_car_data')
        
        for index, car in enumerate(car_list):

            """
            options  = []
            add_options = []
            options.append(car['옵션'].split('\n'))
            add_options.append(car['추가옵션'].split('\n'))
            """

            dict_data = {}
            opt_list = car['옵션'].split('\n')
            for i, opt in enumerate(opt_list):
                if opt == "":
                    opt_list.remove(opt_list[i])

            add_list = car['추가옵션'].split('\n')
            for i, opt in enumerate(add_list):
                if opt == "":
                    add_list.remove(add_list[i])

            dict_data['옵션'] = opt_list
            dict_data['추가옵션'] = add_list
            json_options = json.dumps(dict_data, ensure_ascii=False)

            my_db = pymysql.connect(host='grdver.xyz',
                                            port=3306,
                                            user='healer',
                                            password='7974',
                                            db='HeyHealer',
                                            charset='utf8',
                                            autocommit=True,
                                            cursorclass=pymysql.cursors.DictCursor)

            sql = "UPDATE heydealer_car_data SET 옵션목록 = %s WHERE url = '{}'".format(car['url'])
            with my_db:
                with my_db.cursor() as cur:
                    cur.execute(sql, (json_options))
                    my_db.commit

            print(str(index) + "/" + str(len(car_list)))

        



if __name__ == '__main__':
    app = EditOption()