import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path='prod.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, 
            name TEXT, 
            phone_number TEXT, 
            reg_date DATETIME)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            pr_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            pr_name TEXT, 
            pr_price REAL, 
            pr_quantity INTEGER, 
            pr_des TEXT, 
            pr_photo TEXT, 
            reg_date DATETIME)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cart (
            user_id INTEGER, 
            pr_id INTEGER, 
            pr_name TEXT, 
            pr_count INTEGER, 
            total_price REAL)''')
        self.conn.commit()


    def add_user(self, user_id, user_name, user_phone_number):
        self.cursor.execute("INSERT INTO users (user_id, name, phone_number, reg_date) VALUES (?, ?, ?, ?);",
                            (user_id, user_name, user_phone_number, datetime.now()))
        self.conn.commit()

    def get_users(self):
        self.cursor.execute("SELECT * FROM users;")
        return self.cursor.fetchall()

    def check_user(self, user_id):
        self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?;", (user_id,))
        return self.cursor.fetchone() is not None

    # Методы для работы с продуктами
    def add_product(self, pr_name, pr_price, pr_quantity, pr_des, pr_photo):
        self.cursor.execute("INSERT INTO products (pr_name, pr_price, pr_quantity, pr_des, pr_photo, reg_date) "
                            "VALUES (?, ?, ?, ?, ?, ?);",
                            (pr_name, pr_price, pr_quantity, pr_des, pr_photo, datetime.now()))
        self.conn.commit()

    def get_all_products(self):
        self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()

    def get_pr_id_name(self):
        self.cursor.execute("SELECT pr_id, pr_name, pr_quantity FROM products")
        return [(i[0], i[1]) for i in self.cursor.fetchall() if i[2] > 0]

    def get_exact_product(self, pr_id):
        self.cursor.execute("SELECT pr_name, pr_price, pr_des, pr_photo FROM products WHERE pr_id=?;", (pr_id,))
        return self.cursor.fetchone()

    def delete_products(self):
        self.cursor.execute("DELETE FROM products")
        self.conn.commit()

    def delete_exact_product(self, pr_id):
        self.cursor.execute("DELETE FROM products WHERE pr_id=?;", (pr_id,))
        self.conn.commit()

    def change_quantity(self, pr_id, new_quantity):
        self.cursor.execute("UPDATE products SET pr_quantity=? WHERE pr_id=?;", (new_quantity, pr_id))
        self.conn.commit()


    def add_to_cart(self, user_id, pr_id, pr_name, pr_count):
        total_price = pr_count * self.get_exact_product(pr_id)[1]
        self.cursor.execute("INSERT INTO cart (user_id, pr_id, pr_name, pr_count, total_price) VALUES (?,?,?,?,?);",
                            (user_id, pr_id, pr_name, pr_count, total_price))
        self.conn.commit()

    def delete_exact_pr_from_cart(self, user_id, pr_id):
        self.cursor.execute("DELETE FROM cart WHERE user_id=? AND pr_id=?;", (user_id, pr_id))
        self.conn.commit()

    def delete_user_cart(self, user_id):
        self.cursor.execute("DELETE FROM cart WHERE user_id=?;", (user_id,))
        self.conn.commit()

    def get_user_cart(self, user_id):
        self.cursor.execute("SELECT pr_name, pr_count, total_price FROM cart WHERE user_id=?;", (user_id,))
        return self.cursor.fetchall()


    def add_test_products(self):
        test_products = [
            ("Продукт 1", 100.0, 10, "Описание 1", "photo1.jpg"),
            ("Продукт 2", 200.0, 5, "Описание 2", "photo2.jpg"),
            ("Продукт 3", 150.0, 20, "Описание 3", "photo3.jpg"),
            ("Продукт 4", 300.0, 8, "Описание 4", "photo4.jpg"),
            ("Продукт 5", 250.0, 12, "Описание 5", "photo5.jpg")
        ]
        self.cursor.executemany('INSERT INTO products (pr_name, pr_price, pr_quantity, pr_des, pr_photo, reg_date) VALUES (?, ?, ?, ?, ?, ?)',
                                [(name, price, quantity, des, photo, datetime.now()) for name, price, quantity, des, photo in test_products])
        self.conn.commit()
        print("Тестовые продукты добавлены в базу данных")


db = Database()


db.add_test_products()
