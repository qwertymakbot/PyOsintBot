from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import config
from data import Data
import texts
import sqlite3 as sq
import logging
from kassa import Kassa

bot = Bot(config.token)
dp = Dispatcher(bot)
kassa = Kassa()

logging.basicConfig(level='DEBUG', filename="logs.log", filemode="w")

kb = ReplyKeyboardMarkup(resize_keyboard=True)
but_profile = KeyboardButton(text='Профиль')
but_commands = KeyboardButton(text='Команды')
but_buy_sub = KeyboardButton(text='Оформить подписку')
kb.add(but_profile, but_commands, but_buy_sub)


async def on_startup(_):
    Data.startup()
    print('Bot is on')


@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):
    print(0)
    text = query.query or 'echo'
    await query.answer(text, cache_time=1, is_personal=True)


@dp.message_handler(lambda message: 'Оформить подписку' == message.text)
async def premium(message: types.Message):
    payment_kb = InlineKeyboardMarkup(row_width=1)
    but1 = InlineKeyboardButton(text='Месяц - 200р', callback_data=f'premium_mini_{message.from_user.id}')
    but2 = InlineKeyboardButton(text='3 месяца - 700р', callback_data=f'premium_medium_{message.from_user.id}')
    but3 = InlineKeyboardButton(text='Полгода- 1000р', callback_data=f'premium_high_{message.from_user.id}')
    but4 = InlineKeyboardButton(text='Вечный доступ - 4000р',
                                callback_data=f'premium_max_{message.from_user.id}')
    payment_kb.add(but1, but2, but3, but4)
    await message.answer('Выберите срок премиума:\n'
                         'У нас сейчас следующие расценки:\n'
                         '200р за месяц\n'
                         '700р за 3 месяца\n'
                         '1000р за полгода\n'
                         '4000р за вечный доступ\n\n'
                         'За подробностями @whoissoee', reply_markup=payment_kb)


@dp.message_handler(lambda message: 'Профиль' == message.text)
async def me(message: types.Message):
    user = Data.get_user_data(int(message.from_user.id))
    premium_user = 'нет' if user[0][3] == 0 else 'да'
    admin = 'нет' if user[0][-1] == 0 else 'да'
    await message.reply(
        text=f'Имя пользователя: @{user[0][2]}\nid: {user[0][0]}\nКоличество запросов: {user[0][4]}\nПремиум: {premium_user}\nАдминистратор: {admin}')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    is_user = Data.check_user(message.from_user.id)
    if is_user:
        await message.answer(
            'Привет! Данный бот позволяет найти чаты в которых присутствует пользователь.'
            ' Вам доступно 3 запроса если хотите увеличить количество запросов вам нужно либо купить их либо купить подписку.'
            ' Для просмотра доступных комманд напишите /help', reply_markup=kb)

    else:
        user = {'id': message.from_user.id, 'username': message.from_user.username,
                'name': message.from_user.first_name, 'premium': 0}
        Data.add_user(user)
        await message.answer(
            'Привет! Данный бот позволяет найти чаты в которых присутствует пользователь. Вам доступно 3 запроса если хотите увеличить количество запросов вам нужно либо купить их либо купить подписку. Для просмотра доступных комманд напишите /help')


@dp.message_handler(lambda message: 'Команды' == message.text or '/help' == message.text)
async def help_cmnd(message: types.Message):
    await message.answer(texts.help_text)


@dp.message_handler(commands=['id'])
async def find_id(message: types.message):
    is_user = Data.check_user(message.from_user.id)
    if is_user:
        is_sub = Data.check_subscribe(message.from_user.id)
        user_reqs = Data.get_user_requests(message.from_user.id)
        if is_sub or user_reqs > 0:
            Data.delete_user_request(message.from_user.id)
            params = message.text.replace('/id', '').strip()
            info = Data.find_by_id(int(params))
            groups = []
            groups_links = []
            if len(info) != 0:
                for item in info:
                    if item['groupname'] in groups:
                        continue
                    else:
                        groups.append(item['groupname'])
                        groups_links.append(item['grouptag'])
                group = groups
                links = '\n'.join(groups_links)
                string = '\n'.join(group)
                await message.answer(
                    f" Имя пользователя: @{info[0]['username']}\n id пользователя: {info[0]['userid']}\n Чаты:\n {string}\n Ссылки на чаты:\n {links}")
            elif len(info) == 0:
                await message.answer(f'Пользователь не найден')
            else:
                await message.answer('Вы что-то сделали не так')
        else:
            await message.answer('Для пробива вам необходимо купить премиум или запросы ')

    else:
        return


@dp.message_handler(commands=['username'])
async def find_username(message: types.message):
    is_user = Data.check_user(message.from_user.id)
    if is_user:
        is_sub = Data.check_subscribe(message.from_user.id)
        user_reqs = Data.get_user_requests(message.from_user.id)
        if is_sub or user_reqs > 0:
            Data.delete_user_request(message.from_user.id)
            params = message.text.replace('/username', '').strip()
            if '@' in params:
                params = params.replace('@', '').strip()
            info = Data.find_by_username(str(params).lower())
            groups = []
            groups_links = []
            if len(info) != 0:
                for item in info:
                    if item['groupname'] in groups:
                        continue
                    else:
                        groups.append(item['groupname'])
                        groups_links.append(item['grouptag'])
                group = groups
                links = '\n'.join(groups_links)
                string = '\n'.join(group)
                await message.answer(
                    f" Имя пользователя: @{info[0]['username']}\n id пользователя: {info[0]['userid']}\n Чаты:\n {string}\n Ссылки на чаты:\n {links}")
            elif len(info) == 0:
                await message.answer(f'Пользователь не найден')
            else:
                await message.answer('Вы что-то сделали не так')
        else:
            await message.answer('Для пробива вам необходимо купить премиум или запросы ')

    else:
        return


@dp.message_handler(lambda message: 'Найти' in message.text)
async def find(message: types.Message):
    is_user = Data.check_user(message.from_user.id)
    if is_user:
        is_sub = Data.check_subscribe(message.from_user.id)
        user_reqs = Data.get_user_requests(message.from_user.id)
        if is_sub or user_reqs > 0:
            Data.delete_user_request(message.from_user.id)
            params = str(message.text).replace('Найти по', '')
            if 'юзернейму' in params:
                params = params.replace('юзернейму', '').strip()
                if '@' in params:
                    params = params.replace('@', '').strip()
                print(params)
                info = Data.find_by_username(params.lower())
                groups = []
                groups_links = []
                if len(info) != 0:
                    for item in info:
                        if item['groupname'] in groups:
                            continue
                        else:
                            groups.append(item['groupname'])
                            groups_links.append(item['grouptag'])
                    group = groups
                    links = '\n'.join(groups_links)
                    string = '\n'.join(group)
                    await message.answer(
                        f" Имя пользователя: @{info[0]['username']}\n id пользователя: {info[0]['userid']}\n Чаты:\n {string}\n Ссылки на чаты:\n {links}")
                elif len(info) == 0:
                    await message.answer(f'Пользователь не найден')
                else:
                    await message.answer('Вы что-то сделали не так')
            elif 'id' in params:
                params = params.replace('id', '').strip()
                info = Data.find_by_id(int(params))
                groups = []
                groups_links = []
                if len(info) != 0:
                    for item in info:
                        if item['groupname'] in groups:
                            continue
                        else:
                            groups.append(item['groupname'])
                            groups_links.append(item['grouptag'])
                    group = groups
                    links = '\n'.join(groups_links)
                    string = '\n'.join(group)
                    await message.answer(
                        f" Имя пользователя: @{info[0]['username']}\n id пользователя: {info[0]['userid']}\n Чаты:\n {string}\n Ссылки на чаты:\n {links}")
                elif len(info) == 0:
                    await message.answer(f'Пользователь не найден')
                else:
                    await message.answer('Вы что-то сделали не так')
        else:
            await message.answer('Для пробива вам необходимо купить премиум или запросы ')
    else:
        return


@dp.message_handler(lambda message: 'Дать запрос' == message.text)
async def add_request_to_user(message: types.Message):
    if message.reply_to_message:
        is_admin = Data.check_admin(message.from_user.id)
        if message.from_user.id == config.owner_id or is_admin:
            user_id = message.reply_to_message.from_user.id
            is_user = Data.check_user(user_id)
            if is_user:
                Data.add_user_request(int(user_id))
                await message.reply('Готово')
            else:
                await message.answer(
                    f'Пользователь @{message.reply_to_message.from_user.username} не зарегистрирован в боте')
        else:
            await message.answer('У вас недостаточно прав')
    else:
        await message.reply('Эта команда должна быть отправлена ответом на сообщение пользователя')


@dp.message_handler(lambda message: 'Забрать запрос' == message.text)
async def add_request_to_user(message: types.Message):
    if message.reply_to_message:
        is_admin = Data.check_admin(message.from_user.id)
        if message.from_user.id == config.owner_id or is_admin:
            user_id = message.reply_to_message.from_user.id
            is_user = Data.check_user(user_id)
            if is_user:
                if Data.delete_user_request(int(user_id)):
                    await message.reply('Готово')
                else:
                    await message.answer('Нельзя запрать запрос так как у пользователя из нет')
            else:
                await message.answer(
                    f'Пользователь @{message.reply_to_message.from_user.username} не зарегистрирован в боте')
        else:
            await message.answer('У вас недостаточно прав')
    else:
        await message.reply('Эта команда должна быть отправлена ответом на сообщение пользователя')


@dp.message_handler(lambda message: 'Дать подписку' == message.text)
async def add_sub(message: types.Message):
    if message.reply_to_message:
        is_admin = Data.check_admin(message.from_user.id)
        if message.from_user.id == config.owner_id or is_admin:
            user_id = message.reply_to_message.from_user.id
            is_user = Data.check_user(user_id)
            if is_user:
                is_sub = Data.check_subscribe(user_id)
                if is_sub:
                    await message.reply('У данного пользователя уже есть подписка')
                else:
                    Data.add_subscribe(int(user_id))
                    await message.reply('Готово')
            else:
                await message.answer(
                    f'Пользователь @{message.reply_to_message.from_user.username} не зарегистрирован в боте')
        else:
            await message.answer('У вас недостаточно прав')
    else:
        await message.reply('Эта команда должна быть отправлена ответом на сообщение пользователя')


@dp.message_handler(lambda message: 'Снять админа' == message.text)
async def delete_admin(message: types.Message):
    if message.reply_to_message:
        if message.from_user.id == config.owner_id:
            user_id = message.reply_to_message.from_user.id
            is_user = Data.check_user(user_id)
            if is_user:
                is_admin = Data.check_admin(user_id)
                if is_admin:
                    Data.delete_admin(user_id)
                    is_admin = Data.check_admin(user_id)
                    if is_admin:
                        await message.reply('Что то пошло не так, попробуйте еще раз')
                    else:
                        await message.answer('Готово')
                else:
                    await message.reply('Данный пользователь не является администратором')
            else:
                await message.answer(
                    f'Пользователь @{message.reply_to_message.from_user.username} не зарегистрирован в боте')
        else:
            await message.answer('У вас недостаточно прав')
    else:
        await message.reply('Эта команда должна быть отправлена ответом на сообщение пользователя')


@dp.message_handler(lambda message: 'Добавить админа' in message.text)
async def add_sub(message: types.Message):
    if message.reply_to_message:
        if message.from_user.id == config.owner_id:
            user_id = message.reply_to_message.from_user.id
            is_user = Data.check_user(user_id)
            if is_user:
                is_admin = Data.check_admin(user_id)
                if is_admin:
                    await message.answer('Данный пользователь уже является администратором')
                else:
                    Data.add_admin(user_id)
                    await message.reply('Готово')
            else:
                await message.answer(
                    f'Пользователь @{message.reply_to_message.from_user.username} не зарегистрирован в боте')
        else:
            await message.answer('У вас недостаточно прав')
    else:
        await message.reply('Эта команда должна быть отправлена ответом на сообщение пользователя')


@dp.message_handler(lambda message: 'Забрать подписку' in message.text)
async def delete_sub(message: types.Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        is_user = Data.check_user(user_id)
        if is_user:
            is_sub = Data.check_subscribe(user_id)
            if is_sub:
                Data.delete_subscribe(user_id)
                await message.reply('Готово')
            else:
                await message.reply('У данного пользователя отсутствует подписка')
        else:
            await message.answer(
                f'Пользователь @{message.reply_to_message.from_user.username} не зарегистрирован в боте')
    else:
        await message.reply('Эта команда должна быть отправлена ответом на сообщение пользователя')


@dp.message_handler(lambda message: 'id' == message.text or 'Id' == message.text)
async def answer_id(message: types.Message):
    await message.answer(f"Ваш id: {message.from_user.id}\n id чата: {message.chat.id}")


@dp.message_handler(lambda message: 'Data' in message.text)
async def data(message: types.Message):
    with sq.connect(config.database) as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users')
        data_ = cur.fetchall()
        await message.answer(text=str(data_))


@dp.message_handler(lambda message: 'Log' in message.text or 'Логи' in message.text)
async def send_log(message: types.message):
    await message.reply_document(open('logs.log', 'rb'))


@dp.callback_query_handler(lambda callback: 'premium_' in callback.data)
async def premium_callbacks(callback: types.CallbackQuery):
    params = callback.data.split('_')
    print(params)
    user_id = params[-1]
    category = params[1]
    if category == 'mini':  
        kb = InlineKeyboardMarkup()
        order_id = Data.generate_order_id()
        link = kassa.generate_link(payment_id=order_id, price=200)
        but = InlineKeyboardButton(text='Клик!', url=link)
        kb.add(but)
        Data.create_order(user_id=callback.from_user.id, premium_type='mini', summ=200)
        await callback.message.answer('Отлично! Для оплаты нажми на кнопку ниже и перейди по ссылке.', reply_markup=kb)
    elif category == 'medium':
        kb = InlineKeyboardMarkup()
        order_id = Data.generate_order_id()
        link = kassa.generate_link(payment_id=order_id, price=700)
        but = InlineKeyboardButton(text='Клик!', url=link)
        kb.add(but)
        Data.create_order(user_id=callback.from_user.id, premium_type='medium', summ=700)
        await callback.message.answer('Отлично! Для оплаты нажми на кнопку ниже и перейди по ссылке.', reply_markup=kb)
    elif category == 'high':
        kb = InlineKeyboardMarkup()
        order_id = Data.generate_order_id()
        link = kassa.generate_link(payment_id=order_id, price=1000)
        but = InlineKeyboardButton(text='Клик!', url=link)
        kb.add(but)
        Data.create_order(user_id=callback.from_user.id, premium_type='high', summ=1000)
        await callback.message.answer('Отлично! Для оплаты нажми на кнопку ниже и перейди по ссылке.', reply_markup=kb)
    elif category == 'max':
        kb = InlineKeyboardMarkup()
        order_id = Data.generate_order_id()
        link = kassa.generate_link(payment_id=order_id, price=4000)
        but = InlineKeyboardButton(text='Клик!', url=link)
        kb.add(but)
        Data.create_order(user_id=callback.from_user.id, premium_type='max', summ=4000)
        await callback.message.answer('Отлично! Для оплаты нажми на кнопку ниже и перейди по ссылке.', reply_markup=kb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
