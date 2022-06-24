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

from workers.databaser import MySQL

from bs4 import BeautifulSoup





datas = MySQL().selectFromTable('heydealer_car_data')

count = 0
for i, v in enumerate(datas):
    if v['json_my_car_damaged'] != None:
        json_file = str(v['json_my_car_damaged']).replace('\\', '').replace('"{', '{').replace('}"', '}')
        j_data = json.loads(json_file)
        j_dump = json.dumps(j_data, ensure_ascii=False)
        url = v['url']
        my_db = pymysql.connect(host='grdver.xyz',
                                                port=3306,
                                                user='healer',
                                                password='7974',
                                                db='HeyHealer',
                                                charset='utf8',
                                                autocommit=True,
                                                cursorclass=pymysql.cursors.DictCursor)

        sql = "UPDATE heydealer_car_data SET json_my_car_damaged = %s WHERE url = '{}'".format(url)
        with my_db:
            with my_db.cursor() as cur:
                cur.execute(sql, j_dump)
                my_db.commit

        print(str(i) + " / " + str(len(datas)))
