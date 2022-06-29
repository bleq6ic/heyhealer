from matplotlib.font_manager import json_load
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
import json

sql = "SELECT * FROM {} ".format(
            'heydealer_car_data')

my_db = pymysql.connect(host='grdver.xyz',
                        port=3306,
                        user='healer',
                        password='7974',
                        db='HeyHealer',
                        charset='utf8',
                        autocommit=True,
                        cursorclass=pymysql.cursors.DictCursor)

with my_db:
    with my_db.cursor() as cur:
        cur.execute(sql)
        car_list = cur.fetchall()

        for value in car_list:

            url = value['url']

            new_list = []
            if value['json_my_car_damaged'] != None:
                json_load = json.loads(value['json_my_car_damaged'])
                
                for i, v in enumerate(json_load['수리비']):
                    new_list.append(json_load['수리비'][v])


            new_json_file = {"내차피해액":new_list}
            json_record = json.dumps(new_json_file, ensure_ascii=False)

            print(json_record)

            save_sql = "UPDATE heydealer_car_data SET json_my_car_damaged = %s WHERE url = '{}'".format(url)
            cur.execute(save_sql, (json_record))
            my_db.commit