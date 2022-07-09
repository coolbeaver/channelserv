import re

import psycopg2
import bs4
import requests

from config_bd import *


class Database:
    def __init__(self):
        self.rate = None
        self.connection = psycopg2.connect(user=user,
                                           password=password,
                                           host=host,
                                           port=port,
                                           database=database)
        self.cursor = self.connection.cursor()

    def insert_table(self, item_tuple):
        insert = 'INSERT INTO sheets (заказ№, стоимость$, стоимость₽, срокпоставки) VALUES (%s, %s, %s, %s)'
        self.cursor.execute(insert, item_tuple)
        self.connection.commit()
        print("Вставка выполнена")

    def update_table(self, item_tuple):
        if len(item_tuple) == 4:
            update_query = 'UPDATE sheets SET стоимость$ = %s, стоимость₽ = %s, срокпоставки = %s WHERE заказ№ = %s'
            self.cursor.execute(update_query, (item_tuple[1], item_tuple[2], item_tuple[3], item_tuple[0]))

        elif len(item_tuple) == 3:
            update_query = 'UPDATE sheets SET стоимость$ = %s, срокпоставки = %s WHERE заказ№ = %s'
            self.cursor.execute(update_query, (item_tuple[1], item_tuple[2], item_tuple[0]))

        self.connection.commit()
        print('Данные обновлены')

    def select_table(self):
        self.cursor.execute("SELECT * from sheets")
        select_data = self.cursor.fetchall()
        return select_data

    def total_order_price(self):
        total = 0
        select_data = self.select_table()
        for i in select_data:
            total += int(i[2])
        return total

    def delete_from_table(self, id):
        delete_query = 'DELETE FROM sheets WHERE заказ№ = %s'
        self.cursor.execute(delete_query, (id,))
        self.connection.commit()
        print('DELETED')

    def compare_table(self, array_sheets):
        self.cursor.execute("SELECT заказ№, стоимость$, срокпоставки from sheets")
        select_data = self.cursor.fetchall()

        if (select_data == array_sheets) is False:
            self.rate = Database.currenty_exchange()
            self.difference_array(array_sheets, select_data)

    @staticmethod
    def currenty_exchange():
        result = requests.get('https://www.cbr.ru/scripts/XML_daily.asp?')
        soup = bs4.BeautifulSoup(result.text, 'xml')
        found_user = soup.findAll('Valute')
        for i in found_user:
            if "USD" in i.text:
                value = i.find('Value')
                return value.text

    def difference_array(self, array1, array2):
        self.rate = Database.currenty_exchange()
        difference_array_1 = [x for x in array1 if x not in array2]
        difference_array_2 = [x for x in array2 if x not in array1]

        for b in difference_array_1:
            for i in difference_array_2:
                if b[0] == i[0]:
                    if b[1] != i[1]:
                        b = b[:2] + (f"{int(int(b[1]) * float(re.sub(',', '.', self.rate)))}",) + b[2:]
                    self.update_table(b)
                    print('update_table')
                    break
            else:
                b = b[:2] + (f"{int(int(b[1]) * float(re.sub(',', '.', self.rate)))}",) + b[2:]
                print(b)
                self.insert_table(b)

        for itr in difference_array_2:
            print(itr)
            for i in difference_array_1:
                if itr[0] == i[0]:
                    break
            else:
                self.delete_from_table(itr[0])



