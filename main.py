from time import sleep
from flask import Flask, render_template
from sheets import Sheets
from bd import Database

import multiprocessing as mp

sheet = Sheets()
db = Database()
db2 = Database()
app = Flask(__name__)


@app.route('/')
def index():
    data_fetchall = db2.select_table()
    data_total = db2.total_order_price()
    return render_template('index.html', data_fetchall=data_fetchall, total=data_total)


def main():
    while True:
        sleep(15)
        sheets_array = Sheets.read_sheets(sheet.creds)
        db.compare_table(sheets_array)


def call(func: callable):
    func()


def multiprocess_run():
    tasks = [main, app.run]
    procs = [mp.Process(target=call, args=(i,)) for i in tasks]
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()


if __name__ == '__main__':
    multiprocess_run()
