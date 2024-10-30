import sqlite3
from datetime import datetime
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        try:
            # Получаем абсолютный путь к директории текущего файла
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Формируем абсолютный путь к файлу базы данных
            db_path = os.path.join(base_dir, 'prod.db')
            logger.info(f"Initializing database at: {db_path}")

            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def create_tables(self):
        try:
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
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def add_user(self, user_id, user_name, user_phone_number):
        try:
            self.cursor.execute(
                "INSERT INTO users (user_id, name, phone_number, reg_date) VALUES (?, ?, ?, ?);",
                (user_id, user_name, user_phone_number, datetime.now())
            )
            self.conn.commit()
            logger.info(f"User added successfully: {user_id}")
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            raise

    def get_users(self):
        try:
            self.cursor.execute("SELECT * FROM users;")
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    def check_user(self, user_id):
        try:
            self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?;", (user_id,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking user: {e}")
            return False

    def add_product(self, pr_name, pr_price, pr_quantity, pr_des, pr_photo):
        try:
            self.cursor.execute(
                "INSERT INTO products (pr_name, pr_price, pr_quantity, pr_des, pr_photo, reg_date) VALUES (?, ?, ?, ?, ?, ?);",
                (pr_name, pr_price, pr_quantity, pr_des, pr_photo, datetime.now())
            )
            self.conn.commit()
            logger.info(f"Product added successfully: {pr_name}")
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            raise

    def get_all_products(self):
        try:
            self.cursor.execute("SELECT * FROM products")
            products = self.cursor.fetchall()
            if not products:
                logger.warning("No products found in database")
            return products
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []

    def get_pr_id_name(self):
        try:
            self.cursor.execute("SELECT pr_id, pr_name, pr_quantity FROM products")
            return [(i[0], i[1]) for i in self.cursor.fetchall() if i[2] > 0]
        except Exception as e:
            logger.error(f"Error getting product IDs and names: {e}")
            return []

    def get_exact_product(self, pr_id):
        try:
            self.cursor.execute("SELECT pr_name, pr_price, pr_des, pr_photo FROM products WHERE pr_id=?;", (pr_id,))
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting exact product: {e}")
            return None

    def delete_products(self):
        try:
            self.cursor.execute("DELETE FROM products")
            self.conn.commit()
            logger.info("All products deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting products: {e}")
            raise

    def delete_exact_product(self, pr_id):
        try:
            self.cursor.execute("DELETE FROM products WHERE pr_id=?;", (pr_id,))
            self.conn.commit()
            logger.info(f"Product deleted successfully: {pr_id}")
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            raise

    def change_quantity(self, pr_id, new_quantity):
        try:
            self.cursor.execute("UPDATE products SET pr_quantity=? WHERE pr_id=?;", (new_quantity, pr_id))
            self.conn.commit()
            logger.info(f"Product quantity updated: ID={pr_id}, New quantity={new_quantity}")
        except Exception as e:
            logger.error(f"Error changing quantity: {e}")
            raise

    def add_to_cart(self, user_id, pr_id, pr_name, pr_count):
        try:
            total_price = pr_count * self.get_exact_product(pr_id)[1]
            self.cursor.execute(
                "INSERT INTO cart (user_id, pr_id, pr_name, pr_count, total_price) VALUES (?,?,?,?,?);",
                (user_id, pr_id, pr_name, pr_count, total_price)
            )
            self.conn.commit()
            logger.info(f"Product added to cart: User={user_id}, Product={pr_name}")
        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            raise

    def delete_exact_pr_from_cart(self, user_id, pr_id):
        try:
            self.cursor.execute("DELETE FROM cart WHERE user_id=? AND pr_id=?;", (user_id, pr_id))
            self.conn.commit()
            logger.info(f"Product removed from cart: User={user_id}, Product ID={pr_id}")
        except Exception as e:
            logger.error(f"Error deleting from cart: {e}")
            raise

    def delete_user_cart(self, user_id):
        try:
            self.cursor.execute("DELETE FROM cart WHERE user_id=?;", (user_id,))
            self.conn.commit()
            logger.info(f"Cart cleared for user: {user_id}")
        except Exception as e:
            logger.error(f"Error deleting user cart: {e}")
            raise

    def get_user_cart(self, user_id):
        try:
            self.cursor.execute("SELECT pr_name, pr_count, total_price FROM cart WHERE user_id=?;", (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting user cart: {e}")
            return []

    def add_test_products(self):
        try:
            # Проверяем, есть ли уже продукты в базе
            if self.get_all_products():
                logger.info("Products already exist in database")
                return

            test_products = [
                ("Продукт 1", 100.0, 10, "Описание 1", "photo1.jpg"),
                ("Продукт 2", 200.0, 5, "Описание 2", "photo2.jpg"),
                ("Продукт 3", 150.0, 20, "Описание 3", "photo3.jpg"),
                ("Продукт 4", 300.0, 8, "Описание 4", "photo4.jpg"),
                ("Продукт 5", 250.0, 12, "Описание 5", "photo5.jpg")
            ]

            self.cursor.executemany(
                'INSERT INTO products (pr_name, pr_price, pr_quantity, pr_des, pr_photo, reg_date) VALUES (?, ?, ?, ?, ?, ?)',
                [(name, price, quantity, des, photo, datetime.now()) for name, price, quantity, des, photo in
                 test_products]
            )
            self.conn.commit()
            logger.info("Test products added successfully")
        except Exception as e:
            logger.error(f"Error adding test products: {e}")
            raise


# Создаем экземпляр базы данных
db = Database()