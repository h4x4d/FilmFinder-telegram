import sqlite3

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from settings import *
from keyboards import *

from requests import post

bot = Bot(token=token, parse_mode='HTML')
dp = Dispatcher(bot)

actions = {}
texts = {}
last_message = {}

conn = sqlite3.connect('date.db')
cur = conn.cursor()


async def execute_results(user_id):
    results = texts[user_id]
    text, page = results[0], results[1]

    r = []

    cur.execute(f'SELECT * FROM subtitles WHERE half_raw_text '
                f'LIKE "%{text}%" LIMIT 5 OFFSET {5 * page}')

    results = cur.fetchall()

    counter = cur.execute(f'SELECT COUNT(text) FROM subtitles WHERE '
                          f'half_raw_text LIKE "%{text}%"').fetchone()[0]

    if results == [[]]:
        await bot.send_message(user_id, 'Ничего не найдено. Попробуйте '
                                        'еще раз!')

        actions[user_id] = 'find_film'
        return

    for result in results:
        film = cur.execute('SELECT * FROM films WHERE '
                           'id = ?', (result[4], )).fetchone()
        a = f'{film[1]}: \n\n{result[0]} --> {result[1]}\n' \
            f'Текст фразы: {result[2]}\n\n' \
            f'О фильме: {film[2]}\n' \
            '-------------------------------------------------------------'
        r.append(a)

    results = f'<b>Найдено {counter} результатов ({counter // 5 + 1} ' \
              f'страниц). ' \
              f'страниц). ' \
              f'Страница №{page + 1}:</b>\n\n' + '\n'.join(r)

    keyboard = InlineKeyboardMarkup()

    if page == 0 and counter // 5 != page:
        keyboard.row(InlineKeyboardButton('➡', callback_data='next_page'))
    elif page == 0 and counter // 5 == page:
        pass
    elif counter // 5 == page:
        keyboard.row(InlineKeyboardButton('⬅', callback_data='prev_page'))
    else:
        keyboard.row(InlineKeyboardButton('⬅', callback_data='prev_page'),
                     InlineKeyboardButton('➡', callback_data='next_page'))

    keyboard.row(InlineKeyboardButton('❌ Скрыть ❌', callback_data='msg_hide'))

    return results, keyboard


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.message):
    user = message.chat.id
    username = message.chat.username

    parameters = {
        'username': username,
        'id': user
    }

    post('https://filmfinder.ru/get_tg', params=parameters)

    await bot.send_message(user, f'Привет {message.chat.first_name}!\n'
                                 f'Этот бот поможет тебе с поиском '
                                 f'фильмов по фразе из них. Используется '
                                 f'база данных более 500 фильмов и 600 '
                                 f'тысяч строк текста.\n\n '
                                 f'Также, у нас есть свой сайт с '
                                 f'расширенным функционалом: '
                                 f'https://filmfinder.ru/',
                           reply_markup=main_keyboard)


@dp.message_handler(content_types=['text'])
async def help_start_command(message: types.message):
    text = message.text
    user = message.chat.id

    if text == '❓ О сервисе ❓':
        await bot.send_message(user, f'Привет {message.chat.first_name}!\n'
                                     f'Этот бот поможет тебе с поиском '
                                     f'фильмов по фразе из них. Используется '
                                     f'база данных более 500 фильмов и 600 '
                                     f'тысяч строк текста.\n\n '
                                     f'Также, у нас есть свой сайт с '
                                     f'расширенным функционалом: '
                                     f'https://filmfinder.ru/')
    elif text == '🔍 Поиск фильмов 🔍':
        await bot.send_message(user, 'Введите цитату для ее поиска по базе:')
        actions[user] = 'find_film'
    elif user in actions:
        action = actions[user]

        if action == 'find_film':
            actions[user] = ''
            half_raw_text = text.lower()
            half_raw_text = half_raw_text.replace(',', '')
            half_raw_text = half_raw_text.replace('.', '')
            half_raw_text = half_raw_text.replace('!', '')
            half_raw_text = half_raw_text.replace('-', '')
            half_raw_text = half_raw_text.replace('?', '')

            texts[user] = [half_raw_text, 0]

            mess, keyboard = await execute_results(user)
            ms = await bot.send_message(user, mess, reply_markup=keyboard)
            if user in last_message and last_message[user]:
                await bot.delete_message(user, last_message[user])
            last_message[user] = ms.message_id


@dp.callback_query_handler(lambda c: True if c.data else False)
async def process_callback_button1(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    user = call.from_user.id

    c_data = call.data

    if c_data == 'next_page':
        texts[user][1] += 1
        mess, keyboard = await execute_results(user)
        await bot.edit_message_text(mess, user, call.message.message_id,
                                    reply_markup=keyboard)
    elif c_data == 'prev_page':
        texts[user][1] -= 1
        mess, keyboard = await execute_results(user)
        await bot.edit_message_text(mess, user, call.message.message_id,
                                    reply_markup=keyboard)

    elif c_data == 'msg_hide':
        await bot.delete_message(user, call.message.message_id)
        last_message[user] = 0
        texts[user] = []


if __name__ == '__main__':
    executor.start_polling(dp)
