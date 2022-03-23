from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row('🔍 Поиск фильмов 🔍')
main_keyboard.row('❓ О сервисе ❓')