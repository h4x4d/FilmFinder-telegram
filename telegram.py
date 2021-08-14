from telebot import TeleBot
import requests
import sqlite3
import os

token = os.getenv('TELEGRAMBOT_TOKEN')
bot = TeleBot(token)
link = 'http://18.118.209.62'


@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        us = message.chat.id
        un = message.chat.username
        res = requests.post(f'{link}/get_tg?username={un}&id={us}').text
        if res == 'nthx':
            bot.send_message(us, 'Вы уже записаны в базу, нет нужды добавлять еще раз')
        elif res == 'thx':
            bot.send_message(us, 'Ваш айди зарегистирован, можно подключать 2FA')
    except Exception as e:
        print(e)
        bot.send_message(us, 'Произошла непридвиденная ошибка.')


@bot.message_handler(commands=['help'])
def help_command(message):
    us = message.chat.id
    bot.send_message(us, 'FilmFinder - бот, созданный для поиска фильмов по тексту, который был в нужном фильме.\n'
                         f'Сайт: {link}\n'
                         f'Комманды:\n'
                         f'/start - зарегистрирует вас в 2FA базе, начнет пользование ботом\n'
                         f'/help - выведет это сообщение еще раз\n'
                         f'/search - поиск фильма по базе FilmFinder')


@bot.message_handler(commands=['search'])
def search(message):
    tx = message.text
    us = message.chat.id
    if tx == '/search':
        bot.send_message(us, 'Хорошо, введите текст, по которому нужно найти фильм.')
    else:
        text = tx[8:].lower()
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM subtitles WHERE text like "%{text}%"')
        results = cur.fetchall()
        for result in results:
            cur.execute(f'SELECT * FROM films WHERE id = {result[4]}')
            film = cur.fetchone()
            a = f'{film[1]}: \n\n{result[0]} --> {result[1]}\n' \
                f'Текст фразы: {result[2]}\n' \
                f'О фильме: {film[2]}\n' \
                f'Рейтинг фильма на Кинопоиске: {film[3]}\n' \
                '-------------------------------------------------------------'
            bot.send_message(us, a)


@bot.message_handler(content_types=['text'])
def search(message):
    tx = message.text
    us = message.chat.id
    text = tx.lower()
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM subtitles WHERE text like "%{text}%"')
    results = cur.fetchall()
    send = []
    a = 0
    for result in results:
        cur.execute(f'SELECT * FROM films WHERE id = {result[4]}')
        film = cur.fetchone()
        a = f'{film[1]}: \n\n{result[0]} --> {result[1]}\n' \
            f'Текст фразы: {result[2]}\n\n' \
            f'О фильме: {film[2]}\n' \
            '-------------------------------------------------------------'
        send.append(a)
        if len(send) == 5:
            bot.send_message(us, '\n'.join(send))
            send = []
    if send:
        bot.send_message(us, '\n'.join(send))
    bot.send_message(us, '! ВНИМАНИЕ !\n'
                         'В базе телеграмма количество фильмов урезано. Пользуйтесь сайтом для регулярного поиска\n'
                         f'Сайт: {link}')


if __name__ == '__main__':
    bot.polling()
