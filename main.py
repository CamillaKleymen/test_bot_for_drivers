import telebot
from telebot import types
from database import db
from buttons import Keyboard
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_TOKEN = '7919571616:AAHXJ3GSWxp4DnrpChOM79cxd9KAm-aTo4g'
bot = telebot.TeleBot(API_TOKEN)


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = "camillakleymen@gmail.com"
EMAIL_HOST_PASSWORD = "zqrz tgqi zgpt yvyp"
EMAIL_RECIPIENT = "camillakleymen@gmail.com"


user_states = {}


def get_user_info(user_id):

    try:
        cursor = db.cursor
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return None


def format_order_email(user_id, cart_items, total):

    user_info = get_user_info(user_id)
    if not user_info:
        return None

    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message_text = f"""
    Новый заказ #{user_id}
    Дата и время: {order_time}

    Информация о покупателе:
    - ID: {user_id}
    - Имя: {user_info[1]}
    - Телефон: {user_info[2]}

    Состав заказа:
    """

    for item in cart_items:
        message_text += f"- {item[0]}: {item[1]} шт. × {item[2] / item[1]}сум = {item[2]}сум\n"

    message_text += f"\nИтоговая сумма заказа: {total}сум"
    return message_text


def send_order_email(user_id, cart_items, total):

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = f'Новый заказ #{user_id} от {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        message_text = format_order_email(user_id, cart_items, total)
        if not message_text:
            logger.error(f"Failed to format email for user {user_id}")
            return False

        msg.attach(MIMEText(message_text, 'plain'))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        logger.info(f"Order email sent successfully for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send order email: {e}")
        return False


@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        if not db.check_user(user_id):
            bot.send_message(
                message.chat.id,
                "Добро пожаловать! Для регистрации введите ваше имя:"
            )
            bot.register_next_step_handler(message, get_name)
        else:
            show_main_menu(message.chat.id)
    except Exception as e:
        logger.error(f"Start error: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")


def get_name(message):
    try:
        user_id = message.from_user.id
        name = message.text.strip()

        if not name or len(name) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, введите корректное имя.")
            bot.register_next_step_handler(message, get_name)
            return

        user_states[user_id] = {"name": name}
        bot.send_message(
            message.chat.id,
            "Теперь отправьте ваш номер телефона:",
            reply_markup=Keyboard.get_phone_number()
        )
        bot.register_next_step_handler(message, get_phone)
    except Exception as e:
        logger.error(f"Name registration error: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")


def get_phone(message):
    try:
        user_id = message.from_user.id
        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()

        if not phone:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте корректный номер телефона.")
            bot.register_next_step_handler(message, get_phone)
            return

        name = user_states[user_id]["name"]
        db.add_user(user_id, name, phone)

        bot.send_message(
            message.chat.id,
            f"Спасибо за регистрацию, {name}!",
            reply_markup=types.ReplyKeyboardRemove()
        )
        show_main_menu(message.chat.id)
    except Exception as e:
        logger.error(f"Phone registration error: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")


def show_main_menu(chat_id):
    try:
        bot.send_message(
            chat_id,
            "Выберите действие:",
            reply_markup=Keyboard.main_menu()
        )
    except Exception as e:
        logger.error(f"Main menu error: {e}")
        bot.send_message(chat_id, "Произошла ошибка при загрузке меню.")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        user_id = call.message.chat.id

        if call.data == "products":
            show_products(call.message)
        elif call.data == "cart":
            show_cart(call.message)
        elif call.data == "mm":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            show_main_menu(call.message.chat.id)
        elif call.data == "clear_cart":
            clear_cart(call.message)
        elif call.data == "order":
            process_order(call.message)
        elif call.data.startswith("add_to_cart_"):
            product_id = int(call.data.split("_")[-1])
            add_to_cart(call.message, product_id)
        elif call.data == "back_to_products":
            show_products(call.message)
        elif call.data == "feedback":
            bot.send_message(call.message.chat.id, "Функция отзывов находится в разработке")
        elif call.data == "support":
            bot.send_message(call.message.chat.id, "Для связи с поддержкой напишите на email: support@example.com")

        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте позже.")


def show_products(message):
    try:
        products = db.get_all_products()
        if not products:
            bot.edit_message_text(
                "К сожалению, товары отсутствуют.",
                message.chat.id,
                message.message_id,
                reply_markup=Keyboard.main_menu()
            )
            return

        keyboard = types.InlineKeyboardMarkup(row_width=1)

        for product in products:
            product_id, name, price = product[0], product[1], product[2]
            button = types.InlineKeyboardButton(
                f"{name} - {price}сум",
                callback_data=f"add_to_cart_{product_id}"
            )
            keyboard.add(button)

        keyboard.add(types.InlineKeyboardButton("Назад", callback_data="mm"))

        bot.edit_message_text(
            "Выберите товар для добавления в корзину:",
            message.chat.id,
            message.message_id,
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Show products error: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при загрузке товаров.")


def add_to_cart(message, product_id):
    try:
        user_id = message.chat.id
        product = db.get_exact_product(product_id)

        if not product:
            bot.send_message(user_id, "Товар не найден.")
            return

        product_name, product_price = product[0], product[1]
        db.add_to_cart(user_id, product_id, product_name, 1)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("Продолжить покупки", callback_data="products"),
            types.InlineKeyboardButton("Перейти в корзину", callback_data="cart")
        )

        bot.send_message(
            user_id,
            f"✅ {product_name} добавлен в корзину",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Add to cart error: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении в корзину.")


def show_cart(message):
    try:
        user_id = message.chat.id
        cart_items = db.get_user_cart(user_id)

        if not cart_items:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("К покупкам", callback_data="products"))
            bot.edit_message_text(
                "Ваша корзина пуста.",
                user_id,
                message.message_id,
                reply_markup=keyboard
            )
            return

        total = sum(item[2] for item in cart_items)
        cart_text = "🛒 Ваша корзина:\n\n"
        for item in cart_items:
            cart_text += f"• {item[0]} x{item[1]} = {item[2]}сум\n"
        cart_text += f"\n💰 Итого: {total}сум"

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("Оформить заказ", callback_data="order"),
            types.InlineKeyboardButton("Очистить корзину", callback_data="clear_cart"),
            types.InlineKeyboardButton("Продолжить покупки", callback_data="products"),
            types.InlineKeyboardButton("Главное меню", callback_data="mm")
        )

        bot.edit_message_text(
            cart_text,
            user_id,
            message.message_id,
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Show cart error: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при просмотре корзины.")


def clear_cart(message):
    try:
        user_id = message.chat.id
        db.delete_user_cart(user_id)

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("К покупкам", callback_data="products"),
            types.InlineKeyboardButton("Главное меню", callback_data="mm")
        )

        bot.edit_message_text(
            "Корзина очищена!",
            user_id,
            message.message_id,
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Clear cart error: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при очистке корзины.")


def process_order(message):
    try:
        user_id = message.chat.id
        cart_items = db.get_user_cart(user_id)

        if not cart_items:
            bot.edit_message_text(
                "Ваша корзина пуста. Добавьте товары перед оформлением заказа.",
                user_id,
                message.message_id,
                reply_markup=Keyboard.main_menu()
            )
            return

        total = sum(item[2] for item in cart_items)

        # Отправляем email с информацией о заказе
        email_sent = send_order_email(user_id, cart_items, total)

        # Очищаем корзину после оформления заказа
        db.delete_user_cart(user_id)

        success_message = f"✅ Ваш заказ на сумму {total}сум успешно оформлен!\n"
        if email_sent:
            success_message += "Подтверждение заказа отправлено администратору.\n"
        success_message += "Мы свяжемся с вами в ближайшее время для подтверждения."

        bot.edit_message_text(
            success_message,
            user_id,
            message.message_id,
            reply_markup=Keyboard.main_menu()
        )
    except Exception as e:
        logger.error(f"Process order error: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при оформлении заказа.")


if __name__ == "__main__":
    try:
        logger.info("Bot started")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")