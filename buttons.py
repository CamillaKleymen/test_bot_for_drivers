from telebot import types


class Keyboard:
    @staticmethod
    def get_phone_number():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        phone_number = types.KeyboardButton("Поделиться контактом", request_contact=True)
        kb.add(phone_number)
        return kb

    @staticmethod
    def main_menu():
        kb = types.InlineKeyboardMarkup(row_width=1)
        products_menu = types.InlineKeyboardButton(text="Продукты", callback_data="products")
        cart_menu = types.InlineKeyboardButton(text="Корзина", callback_data="cart")
        feedback = types.InlineKeyboardButton(text="Оставить отзыв", callback_data="feedback")
        support = types.InlineKeyboardButton(text="Тех.поддержка", callback_data="support")
        kb.add(products_menu, cart_menu, feedback, support)
        return kb

    @staticmethod
    def products_menu(actual_products):
        kb = types.InlineKeyboardMarkup(row_width=3)
        back = types.InlineKeyboardButton(text="Назад", callback_data="mm")
        all_products = [types.InlineKeyboardButton(text=product[1], callback_data=product[0])
                        for product in actual_products]
        kb.add(*all_products)
        kb.row(back)
        return kb

    @staticmethod
    def exact_product(current_amount=1, plus_or_minus=""):
        kb = types.InlineKeyboardMarkup(row_width=3)
        back = types.InlineKeyboardButton(text="Назад", callback_data="back")
        plus = types.InlineKeyboardButton(text="➕", callback_data="plus")
        minus = types.InlineKeyboardButton(text="➖", callback_data="minus")

        if plus_or_minus == "plus":
            current_amount += 1
        elif plus_or_minus == "minus" and current_amount > 1:
            current_amount -= 1

        count = types.InlineKeyboardButton(text=f"{current_amount}", callback_data=str(current_amount))
        add_to_cart = types.InlineKeyboardButton(text="Добавить в корзину", callback_data="to_cart")

        kb.add(minus, count, plus)
        kb.row(add_to_cart)
        kb.row(back)
        return kb

    @staticmethod
    def get_cart_kb():
        kb = types.InlineKeyboardMarkup(row_width=1)
        clear = types.InlineKeyboardButton("Очистить корзину", callback_data="clear_cart")
        order = types.InlineKeyboardButton("Оформить заказ", callback_data="order")
        back = types.InlineKeyboardButton("Назад", callback_data="mm")
        kb.add(clear, order, back)
        return kb

    @staticmethod
    def get_location():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        location = types.KeyboardButton("Отправить локацию", request_location=True)
        kb.add(location)
        return kb

    @staticmethod
    def main_menu_buttons():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        products_button = types.KeyboardButton("📦 Продукты")
        cart_button = types.KeyboardButton("🛒 Корзина")
        checkout_button = types.KeyboardButton("✅ Оформить заказ")
        markup.add(products_button, cart_button, checkout_button)
        return markup

    @staticmethod
    def product_buttons(products):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for product in products:
            button = types.KeyboardButton(f"{product[1]} - {product[2]} руб. (ID: {product[0]})")
            markup.add(button)
        return markup

# Пример использования класса
# keyboard = Keyboard()
# main_menu_kb = keyboard.main_menu()
