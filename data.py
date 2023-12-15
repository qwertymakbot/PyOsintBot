import csv
import sqlite3
import os
import config
from pathlib import Path

source = 'res'
files = []


class Data():

    def __init__(self):
        ...

    @staticmethod
    def startup():
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                premium INTEGER,
                requests INTEGER,
                admin INTEGER
                )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS orders(
                order_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                summ INTEGER,
                premium_type TEXT,
                payment_status TEXT DEFAULT "В обработке"
                )''')
            
        for filename in os.listdir(source):
            files.append(f"res/{filename}")
    
    @staticmethod 
    def add_user(user: dict):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            params = [user['id'], user['name'], user['username'], user['premium'], 3, 0]
            cur.execute('INSERT INTO users VALUES(?,?,?,?,?,?)', params)

    @staticmethod
    def get_user_data(id: int) -> dict():
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE id = ?', [id])
            info = cur.fetchall()
            #user = {'id': info[0], 'name': info[1], 'username': info[2], 'premium': info[3]}
            return info################

    @staticmethod
    def find_by_username(username: str) -> list():
        """Возвращает список со словарями, значения в словарях могут повторяться."""
        result = []
        for filename in files:
            with open(filename, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=',')
                for row in reader:
                    if str(row['username'].lower()) != '':
                        if str(row['username']).lower() == username:
                            result.append(row)
                        else:
                            continue
        return result
    
    @staticmethod
    def find_by_id(id: int) -> list():
        result = []
        for filename in files:
            with open(filename, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=',')
                for row in reader:
                    if int(row['userid'].lower()) != '':
                        if int(row['userid']) == id:
                            result.append(row)
                        else:
                            continue
        return result

    @staticmethod
    def add_subscribe(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE users SET premium = ? WHERE id = ?', [True, user_id])
            result = cur.fetchall()

    @staticmethod
    def delete_subscribe(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE users SET premium = ? WHERE id = ?', [0, user_id])

    @staticmethod
    def check_subscribe(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT premium FROM users WHERE id = ?', [user_id])
            subscribe = cur.fetchall()
            return True if subscribe[0][0] == 1 else False

    @staticmethod
    def check_user(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE id = ?', [user_id])
            user = cur.fetchall()
            return True if len(user) != 0 else False

    @staticmethod
    def get_user_requests(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT requests FROM users WHERE id = ?', [user_id])
            reqs = cur.fetchall()
            reqs = reqs[0][0]
            return reqs


    @staticmethod
    def delete_user_request(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT requests FROM users WHERE id = ?', [user_id])
            reqs = cur.fetchall()
            reqs = int(reqs[0][0])
            if reqs > 0:
                cur.execute('UPDATE users SET requests = ? WHERE id = ?', [reqs - 1, user_id])
                return True
            else:
                return False

    @staticmethod
    def add_user_request(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT requests FROM users WHERE id = ?', [user_id])
            reqs = cur.fetchall()
            reqs = int(reqs[0][0])
            cur.execute('UPDATE users SET requests = ? WHERE id = ?', [reqs + 1, user_id])

    @staticmethod
    def add_admin(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT admin FROM users WHERE id = ?', [user_id])
            info = cur.fetchall()
            info = info
            cur.execute('UPDATE users SET admin = ? WHERE id = ?', [1, user_id])
            conn.commit()
            cur.execute('SELECT admin FROM users WHERE id = ?', [user_id])
            info = cur.fetchall()
            return bool(info[0][0])
        
    @staticmethod
    def delete_admin(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT admin FROM users WHERE id = ?', [user_id])
            cur.execute('UPDATE users SET admin = ? WHERE id = ?', [0, user_id])
            cur.execute('SELECT admin FROM users WHERE id = ?', [user_id])
            info = cur.fetchall()
            return bool(info[0][0])
            
    @staticmethod
    def check_admin(user_id):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT admin FROM users WHERE id = ?', [user_id])
            info = cur.fetchall()
            is_admin = True if info[0][0] == 1 else False 
            return True if is_admin else False
        
    @staticmethod
    def generate_order_id():
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT order_id FROM orders')
            orders_id = cur.fetchall()
            if len(orders_id) == 0:
                return 1
            else:
                result = int(orders_id[-1][-1]) + 1
                return result
            
    @staticmethod
    def create_order(user_id, summ, premium_type, payment_status='В обработке'):
        with sqlite3.connect(config.database) as conn:
            cur = conn.cursor()
            order_id = Data.generate_order_id()
            cur.execute('INSERT INTO orders VALUES(?,?,?,?,?)', [order_id, user_id, summ, premium_type, payment_status])

        
    
            





def main():
    Data.startup() 


    print(Data.delete_admin(config.owner_id))
    print(Data.check_admin(config.owner_id))
    print(Data.add_admin(config.owner_id))
    print(Data.check_admin(config.owner_id))


if __name__ == '__main__':
    main()
