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
        kb = types.InlineKeyboardMarkup(row_width=2)
        products_menu = types.InlineKeyboardButton(text="📦 Продукты", callback_data="products")
        cart_menu = types.InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")
        feedback = types.InlineKeyboardButton(text="📝 Отзыв", callback_data="feedback")
        support = types.InlineKeyboardButton(text="🔧 Поддержка", callback_data="support")
        kb.add(products_menu, cart_menu)
        kb.row(feedback, support)
        return kb

    @staticmethod
    def get_location():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        location = types.KeyboardButton("Отправить локацию", request_location=True)
        kb.add(location)
        return kb

    @staticmethod
    def products_menu(products):
        kb = types.InlineKeyboardMarkup(row_width=1)
        for product in products:
            product_id, name, price = product[0], product[1], product[2]
            button = types.InlineKeyboardButton(
                f"📦 {name} - {price}сум",
                callback_data=f"product_{product_id}"
            )
            kb.add(button)
        back = types.InlineKeyboardButton(text="◀️ Назад", callback_data="mm")
        kb.row(back)
        return kb

    @staticmethod
    def cart_menu(cart_items):
        kb = types.InlineKeyboardMarkup(row_width=2)
        if cart_items:
            order = types.InlineKeyboardButton("✅ Оформить", callback_data="order")
            clear = types.InlineKeyboardButton("🗑 Очистить", callback_data="clear_cart")
            kb.add(order, clear)

        continue_shopping = types.InlineKeyboardButton("🛍 К покупкам", callback_data="products")
        back = types.InlineKeyboardButton("◀️ Главное меню", callback_data="mm")
        kb.row(continue_shopping)
        kb.row(back)
        return kb

    @staticmethod
    def product_detail(product_id):
        kb = types.InlineKeyboardMarkup(row_width=2)
        add_to_cart = types.InlineKeyboardButton("🛒 В корзину", callback_data=f"add_to_cart_{product_id}")
        back = types.InlineKeyboardButton("◀️ Назад", callback_data="products")
        kb.add(add_to_cart, back)
        return kb