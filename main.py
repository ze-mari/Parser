"""
Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)] on win32

Для выполнение запросы нужно библиотека requests
можно устоновить с помощью команды:
pip install requests

Для удобного парсинга нужно библиотека bs4:
pip install beautifulsoup4

Для работы с базы данных mysql.connector
устанавливется вместе с MySQL
"""

import requests
import mysql.connector as mysql
from bs4 import BeautifulSoup


db = mysql.connect(
    host="localhost",
    port=3306,
    user="univer",
    passwd="univer",
)

print(db)

cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS lawyers")

cursor.execute("USE lawyers")

cursor.execute("CREATE TABLE IF NOT EXISTS main (ree_number VARCHAR(32) NOT NULL PRIMARY KEY, "
               "family VARCHAR(255), "
               "name_ VARCHAR(255), "
               "fathers_name VARCHAR(255), "
               "tel VARCHAR(32), "
               "address VARCHAR(1000))")

for i in range(20, 21):
    res = requests.get(
        f"http://lawyers.minjust.ru/lawyers?fullName=&registerNumber="
        f"&identityCard=&status=1&orgForm=&regCode=&page={i}")
    soup = BeautifulSoup(res.text, 'html.parser')
    tbody = soup.tbody
    rows = tbody.find_all('tr')
    del res
    del soup
    del tbody
    for row in rows:
        lawyer_page = row.find('a')['href']
        lawyer_res = requests.get(f"http://lawyers.minjust.ru/{lawyer_page}")
        lawyer_soup = BeautifulSoup(lawyer_res.text, 'html.parser')
        name = lawyer_soup.find('div', attrs={'id': "forms"}).span
        labels = lawyer_soup.find_all('p', attrs={'class': "row label"})
        del lawyer_page
        del lawyer_res
        del lawyer_soup
        address = None
        tel = None
        ree_number = None
        for label in labels:
            if label.string == "Реестровый номер:":
                ree_number = label.find_next_sibling('p')
            elif label.string == "Адрес:":
                address = label.find_next_sibling('p')
            elif label.string == "Телефон:":
                tel = label.find_next_sibling('p')
                break

        name_list = name.string.split()
        if len(name_list) > 3:
            name_list.pop(1)

        cursor.execute("INSERT INTO main (ree_number, family, name_, fathers_name, tel, address) "
                       "VALUES(%s, %s, %s, %s, %s, %s)",
                       (str(ree_number.string), str(name_list[0]), str(name_list[1]),
                        str(name_list[2]), str(tel.string), str(address.string)))
        db.commit()
        print(str(ree_number.string), str(name_list[0]), str(name_list[1]),
              str(name_list[2]), str(tel.string), str(address.string))
