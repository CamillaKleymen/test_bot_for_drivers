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

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация бота и email
API_TOKEN = '7792092390:AAFR9KZDvsehIz03fkBeUp2Kb024tGrC3j4'
bot = telebot.TeleBot(API_TOKEN)

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = "camillakleymen@gmail.com"
EMAIL_HOST_PASSWORD = "zqrz tgqi zgpt yvyp"
EMAIL_RECIPIENT = "camillakleymen@gmail.com"

# Временное хранилище состояний пользователей
user_states = {}


def get_user_info(user_id):
    """Получение информации о пользователе из базы данных"""
    try:
        cursor = db.cursor
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return None


def format_order_email(user_id, cart_items, total):
    """Форматирование email сообщения для заказа"""
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
    """Отправка email с информацией о заказе"""
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
    """Обработчик команды /start"""
    try:
        user_id = message.from_user.id
        if not db.check_user(user_id):
            bot.send_message(
                message.chat.id,
                "👋 Добро пожаловать! Для регистрации введите ваше имя:"
            )
            bot.register_next_step_handler(message, get_name)
        else:
            show_main_menu(message.chat.id)
    except Exception as e:
        logger.error(f"Start error: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте позже.")


def get_name(message):
    """Обработчик получения имени пользователя"""
    try:
        user_states[message.from_user.id] = {'name': message.text}
        bot.send_message(
            message.chat.id,
            "📱 Пожалуйста, поделитесь вашим номером телефона:",
            reply_markup=Keyboard.get_phone_number()
        )
        bot.register_next_step_handler(message, get_phone)
    except Exception as e:
        logger.error(f"Get name error: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка. Пожалуйста, попробуйте /start снова.")


def get_phone(message):
    """Обработчик получения номера телефона"""
    try:
        user_id = message.from_user.id

        if message.contact is not None:
            phone = message.contact.phone_number
        else:
            phone = message.text

        name = user_states[user_id]['name']
        db.add_user(user_id, name, phone)

        if user_id in user_states:
            del user_states[user_id]

        remove_keyboard = types.ReplyKeyboardRemove()

        welcome_text = f"✅ Спасибо за регистрацию, {name}!\n\n" \
                       f"🛍 Добро пожаловать в наш магазин!\n" \
                       f"Выберите раздел из меню ниже:"

        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=remove_keyboard
        )
        show_main_menu(message.chat.id)

    except Exception as e:
        logger.error(f"Get phone error: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при регистрации. Пожалуйста, попробуйте /start снова.",
            reply_markup=types.ReplyKeyboardRemove()
        )


def show_main_menu(chat_id):
    """Отображение главного меню"""
    try:
        bot.send_message(
            chat_id,
            "📋 Главное меню:",
            reply_markup=Keyboard.main_menu()
        )
    except Exception as e:
        logger.error(f"Show main menu error: {e}")
        bot.send_message(chat_id, "❌ Произошла ошибка. Попробуйте позже.")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик всех callback запросов"""
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if call.data == "mm":
            bot.edit_message_text(
                "📋 Главное меню:",
                chat_id,
                message_id,
                reply_markup=Keyboard.main_menu()
            )

        elif call.data == "products":
            products = db.get_all_products()
            if not products:
                bot.edit_message_text(
                    "😔 К сожалению, товары отсутствуют.",
                    chat_id,
                    message_id,
                    reply_markup=Keyboard.main_menu()
                )
            else:
                bot.edit_message_text(
                    "🛍 Выберите товар:",
                    chat_id,
                    message_id,
                    reply_markup=Keyboard.products_menu(products)
                )

        elif call.data.startswith("product_"):
            product_id = int(call.data.split("_")[1])
            product = db.get_exact_product(product_id)
            if product:
                name, price, description, photo = product
                text = f"📦 {name}\n💰 Цена: {price}сум\n📝 {description}"
                bot.edit_message_text(
                    text,
                    chat_id,
                    message_id,
                    reply_markup=Keyboard.product_detail(product_id)
                )

        elif call.data.startswith("add_to_cart_"):
            product_id = int(call.data.split("_")[3])
            product = db.get_exact_product(product_id)
            if product:
                name = product[0]
                db.add_to_cart(chat_id, product_id, name, 1)
                bot.answer_callback_query(call.id, f"✅ {name} добавлен в корзину")
                products = db.get_all_products()
                bot.edit_message_text(
                    "🛍 Выберите товар:",
                    chat_id,
                    message_id,
                    reply_markup=Keyboard.products_menu(products)
                )

        elif call.data == "cart":
            cart_items = db.get_user_cart(chat_id)
            if not cart_items:
                bot.edit_message_text(
                    "🛒 Ваша корзина пуста",
                    chat_id,
                    message_id,
                    reply_markup=Keyboard.cart_menu(cart_items)
                )
            else:
                total = sum(item[2] for item in cart_items)
                cart_text = "🛒 Ваша корзина:\n\n"
                for item in cart_items:
                    cart_text += f"• {item[0]} x{item[1]} = {item[2]}сум\n"
                cart_text += f"\n💰 Итого: {total}сум"
                bot.edit_message_text(
                    cart_text,
                    chat_id,
                    message_id,
                    reply_markup=Keyboard.cart_menu(cart_items)
                )

        elif call.data == "clear_cart":
            db.delete_user_cart(chat_id)
            bot.edit_message_text(
                "🗑 Корзина очищена!",
                chat_id,
                message_id,
                reply_markup=Keyboard.cart_menu([])
            )

        elif call.data == "order":
            cart_items = db.get_user_cart(chat_id)
            if cart_items:
                total = sum(item[2] for item in cart_items)
                if send_order_email(chat_id, cart_items, total):
                    db.delete_user_cart(chat_id)
                    bot.edit_message_text(
                        f"✅ Ваш заказ на сумму {total}сум успешно оформлен!\n"
                        "Мы свяжемся с вами в ближайшее время для подтверждения.",
                        chat_id,
                        message_id,
                        reply_markup=Keyboard.main_menu()
                    )
                else:
                    bot.edit_message_text(
                        "❌ Произошла ошибка при оформлении заказа. Попробуйте позже.",
                        chat_id,
                        message_id,
                        reply_markup=Keyboard.cart_menu(cart_items)
                    )

        elif call.data == "feedback":
            bot.edit_message_text(
                "📝 Чтобы оставить отзыв, напишите его в следующем сообщении:",
                chat_id,
                message_id
            )
            bot.register_next_step_handler(call.message, process_feedback)

        elif call.data == "support":
            bot.edit_message_text(
                "🔧 Служба поддержки:\n\n"
                "📞 Телефон: +998 XX XXX XX XX\n"
                "✉️ Email: support@example.com\n\n"
                "Время работы: 9:00 - 18:00",
                chat_id,
                message_id,
                reply_markup=Keyboard.main_menu()
            )

        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка. Попробуйте позже.")


def process_feedback(message):
    """Обработчик получения отзыва"""
    try:
        feedback_text = f"📝 Новый отзыв от пользователя {message.from_user.id}:\n\n{message.text}"

        # Отправка отзыва на email администратора
        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = f'Новый отзыв от пользователя #{message.from_user.id}'
        msg.attach(MIMEText(feedback_text, 'plain'))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        bot.send_message(
            message.chat.id,
            "✅ Спасибо за ваш отзыв! Мы обязательно его рассмотрим.",
            reply_markup=Keyboard.main_menu()
        )
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при отправке отзыва. Попробуйте позже.",
            reply_markup=Keyboard.main_menu()
        )


if __name__ == "__main__":
    try:
        # Добавляем тестовые продукты при запуске
        db.add_test_products()
        logger.info("Bot started")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")