import pymysql.cursors
import pymysql
from IPython.display import display
import pandas as pd
from PyQt5.QtCore import *


class MySQL(QObject):
    def __init__(self):
        super().__init__()
        self.my_db = pymysql.connect(host='grdver.xyz', 
                                port=3306, 
                                user='healer', 
                                password='7974',
                                db='HeyHealer', 
                                charset='utf8', 
                                autocommit=True, 
                                cursorclass=pymysql.cursors.DictCursor)

    def selectFromTable(self, table_name):

        sql = 'SELECT * FROM {}'.format(table_name)

        with self.my_db:
            with self.my_db.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    def selectWhereColumn(self, table_name, column, key):

        sql = "SELECT * FROM {} WHERE {} = %s".format(table_name, column)

        with self.my_db:
            with self.my_db.cursor() as cur:
                cur.execute(sql, (key))
                return cur.fetchall()

    def deleteWhereColumn(self, table_name, column, key):

        sql = "DELETE FROM {} WHERE {} = %s".format(table_name, column)

        with self.my_db:
            with self.my_db.cursor() as cur:
                cur.execute(sql, (key))
                self.my_db.commit
    