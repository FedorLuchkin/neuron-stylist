import asyncio
from datetime import datetime
import logging
import numpy as np
import os
import shutil
import sys
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import path_editor
from backend import secure_file_open as of
from backend import secure_file_save as sf
import subprocess
from frontend.translations import translate as t

logging.basicConfig(filename='sessions.log', encoding='utf-8', level=logging.DEBUG)

if len(sys.argv) != 2:
    logging.error({'type': 'bot_starting', 'data': 'one argument (token) expected'})
else:
    logging.debug({'type': 'bot_starting', 'data': 'bot was started'})
    token = sys.argv[1]
    img_num = 4
    user_status_path = 'frontend/users_status.npy'
    queue_path = 'backend/queue.npy'
    language_path = 'frontend/translations/users_language.npy'
    fit_progress_path = 'backend/fit_progress.npy'
    admins_path = 'backend/admins.npy'

    if os.path.exists(user_status_path):
        status_dict = of.open_file(user_status_path)
    else:
        status_dict = dict()
        np.save(user_status_path, status_dict)
        logging.debug({'type': 'bot_starting', 'data': 'status_dict was created'})

    if os.path.exists(language_path):
        language_dict = of.open_file(language_path)
    else:
        language_dict = dict()
        np.save(language_path, language_dict)
        logging.debug({'type': 'bot_starting', 'data': 'language_dict was created'})

    if os.path.exists(admins_path):
        admin_dict = of.open_file(admins_path)
    else:
        admin_dict = dict()
        np.save(admins_path, admin_dict)
        logging.debug({'type': 'bot_starting', 'data': 'admin_dict was created'})

    empty_dict = dict()
    np.save(queue_path, empty_dict)
    logging.debug({'type': 'bot_starting', 'data': 'queue_dict was created'})
    np.save(fit_progress_path, empty_dict)
    logging.debug({'type': 'bot_starting', 'data': 'fit_progress_dict was created'})

    bot = AsyncTeleBot(token)


    async def result_waiting(message):
        global bot
        global status_dict
        global language_dict
        global img_num
        global user_status_path

        user_id = str(message.from_user.id)
        result_path = 'telegram_users/' + user_id + \
            '/result/result' + str(img_num - 1) +'.png'
        result_status = False
        while not result_status and status_dict[user_id] == 'processing':
            result_status = os.path.exists(result_path)
            await asyncio.sleep(5)

        if result_status and status_dict[user_id] == 'processing': 
            photo_list = list()
            for i in range(0, img_num):
                result_path = 'telegram_users/' + str(message.from_user.id) + \
                    '/result/result' + str(i) +'.png'
                photo = telebot.types.InputMediaPhoto(open(result_path, 'rb'))
                photo_list.append(photo)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'start'))
            button2 = types.KeyboardButton(t.translate(language_dict[user_id], 'examples_button'))
            button3 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
            markup.add(button1, button2, button3)

            result_path = 'telegram_users/' + str(message.from_user.id) + '/result'
            while os.path.exists(result_path):
                try:
                    await bot.send_media_group(message.chat.id, photo_list)
                    status_dict[user_id] = 'beginning'
                    sf.save_file(user_status_path, user_id, 'beginning')

                    del_path = 'telegram_users/' + str(message.from_user.id)
                    if os.path.exists(del_path):
                        shutil.rmtree(del_path, ignore_errors=True)
                except RuntimeError:
                    logging.error({'type': 'result_sending_try', 'data': {'user_id': user_id, 'time': str(datetime.now())}})
            await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'ready'), reply_markup=markup)


    @bot.message_handler(commands='start')
    async def start(message):
        global language_dict
        global status_dict
        global user_status_path
        
        user_id = str(message.from_user.id)

        queue_dict = of.open_file(queue_path)
        if len(queue_dict) > 0 and user_id in queue_dict.keys():
            queue_dict[user_id] = -1
            sf.save_file(queue_path, user_id, -1)

        del_path = 'telegram_users/' + user_id + '/result'
        if os.path.exists(del_path):
            shutil.rmtree(del_path, ignore_errors=True)

        logging.info({'type': 'user_status', 'data': {'user_id': user_id, 'status': 'cancel_by_using_/start_command', 'time': str(datetime.now())}})

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton('en')
        button2 = types.KeyboardButton('ru')
        markup.add(button1, button2)
        await bot.send_message(message.chat.id, 'сhoose language/выберите язык', reply_markup=markup)
        status_dict[user_id] = 'language'
        sf.save_file(user_status_path, user_id, 'language')


    @bot.message_handler(content_types=['text'])
    async def get_user_text(message):
        global status_dict
        global language_dict
        global img_num
        global user_status_path
        global queue_path
        global language_path

        user_id = str(message.from_user.id)
        if status_dict[user_id] == 'language' and (message.text == 'en' or message.text == 'ru'):
            language_dict[user_id] = message.text
            sf.save_file(language_path, user_id, message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)


            button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'start'))
            button2 = types.KeyboardButton(t.translate(language_dict[user_id], 'examples_button'))
            button3 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
            markup.add(button1, button2, button3)
            await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'start_message'), reply_markup=markup)
            status_dict[user_id] = 'beginning'
            sf.save_file(user_status_path, user_id, 'beginning')


        if message.text == 'statuses' and message.chat.id in of.open_file(admins_path):
            await bot.send_message(message.chat.id, str(status_dict))

        elif message.text == 'languages' and message.chat.id in of.open_file(admins_path):
            await bot.send_message(message.chat.id, str(language_dict))

        elif message.text == 'queue' and message.chat.id in of.open_file(admins_path):
            if os.path.exists(queue_path):
                queue_dict = of.open_file(queue_path)
                await bot.send_message(message.chat.id, str(queue_dict))

        elif status_dict[user_id] == 'content' or status_dict[user_id] == 'style':
            if message.text != t.translate(language_dict[user_id], 'back'):
                await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'not_image'))

        elif message.text == t.translate(language_dict[user_id], 'examples_button'):
            await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'examples'))

        elif message.text == t.translate(language_dict[user_id], 'start'):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
            markup.add(button1)
            await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'send_content'), reply_markup=markup)
            status_dict[user_id] = 'content'
            sf.save_file(user_status_path, user_id, 'content')

        elif message.text == t.translate(language_dict[user_id], 'styling'):
            del_path = 'telegram_users/' + user_id + '/result'
            if os.path.exists(del_path):
                shutil.rmtree(del_path, ignore_errors=True)
            content_path = 'telegram_users/' + \
                str(message.from_user.id) + '/content/content.png'
            style_path = 'telegram_users/' + \
                str(message.from_user.id) + '/style/style.png'
            content_status = os.path.exists(content_path)
            style_status = os.path.exists(style_path)
            if not (content_status and style_status):
                if not content_status:
                    await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'content_not_found'))
                if not style_status:
                    await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'style_not_found'))
            else:
                queue_dict = of.open_file(queue_path)
                queue_keys = list(queue_dict.keys())
                if len(queue_dict) == 0 or (len(queue_keys) == 1 and queue_keys[0] == user_id):
                    queue_dict[user_id] = 1
                    sf.save_file(queue_path, user_id, 1)
                else:
                    queue_dict[user_id] = 0
                    sf.save_file(queue_path, user_id, 0)

                subprocess.Popen(
                    ["python", "backend/neuron_stylist.py", user_id])

                status_dict[user_id] = 'processing'
                sf.save_file(user_status_path, user_id, 'processing')

                future = asyncio.ensure_future(result_waiting(message))

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'cancel'))
                button2 = types.KeyboardButton(t.translate(language_dict[user_id], 'place_in_queue_button'))
                markup.add(button1, button2)
                await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'wait'), reply_markup=markup)

        elif message.text == t.translate(language_dict[user_id], 'cancel') and status_dict[user_id] == 'processing':
            queue_dict = of.open_file(queue_path)
            if len(queue_dict) > 0 and user_id in queue_dict.keys():
                queue_dict[user_id] = -1
                sf.save_file(queue_path, user_id, -1)

            del_path = 'telegram_users/' + user_id + '/result'
            if os.path.exists(del_path):
                shutil.rmtree(del_path, ignore_errors=True)
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=1)
            button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'styling'))
            button2 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
            markup.add(button1, button2)
            await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'can_start'), reply_markup=markup)
            status_dict[user_id] = 'ready'
            sf.save_file(user_status_path, user_id, 'ready')

        elif message.text == t.translate(language_dict[user_id], 'place_in_queue_button') and status_dict[user_id] == 'processing':
            queue_dict = of.open_file(queue_path)
            fit_progress_dict = of.open_file(fit_progress_path)
            if len(queue_dict) > 0:
                try:
                    queue_list = list(queue_dict.keys())
                    place_in_queue = str(queue_list.index(user_id) + 1)
                except ValueError:
                    logging.error({'type': 'user_is_not_in_queue_dict', 'data': {'queue_dict': queue_dict, 'user_id': user_id}})
                if user_id in fit_progress_dict.keys():
                    progress = '\n' + t.translate(language_dict[user_id], 'progress') + str(of.open_file(fit_progress_path)[user_id]) + '%'
                else:
                    progress = ''
                await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'place_in_queue') + \
                    place_in_queue + progress)

        elif message.text != t.translate(language_dict[user_id], 'back') and message.text != 'en' and message.text != 'ru':
            await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'unknown'))

        if message.text == t.translate(language_dict[user_id], 'back'):
            if status_dict[user_id] == 'ready':
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
                markup.add(button1)
                await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'send_style'), reply_markup=markup)
                status_dict[user_id] = 'style'
                sf.save_file(user_status_path, user_id, 'style')
            elif status_dict[user_id] == 'style':
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
                markup.add(button1)
                await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'send_content'), reply_markup=markup)
                status_dict[user_id] = 'content'
                sf.save_file(user_status_path, user_id, 'content')
            elif status_dict[user_id] == 'content':
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'start'))
                button2 = types.KeyboardButton(t.translate(language_dict[user_id], 'examples_button'))
                button3 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
                markup.add(button1, button2, button3)
                await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'start_message'), reply_markup=markup)
                status_dict[user_id] = 'beginning'
                sf.save_file(user_status_path, user_id, 'beginning')
            elif status_dict[user_id] == 'beginning':
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton('en')
                button2 = types.KeyboardButton('ru')
                markup.add(button1, button2)
                await bot.send_message(
                    message.chat.id, 'сhoose language/выберите язык', reply_markup=markup)
                status_dict[user_id] = 'language'
                sf.save_file(user_status_path, user_id, 'language')    

    @bot.message_handler(content_types=['photo'])
    async def get_user_photo(message):
        global status_dict
        global user_status_path

        user_id = str(message.from_user.id)

        if status_dict[user_id] == 'content' or status_dict[user_id] == 'style':
            os.makedirs('telegram_users', exist_ok=True)
            os.chdir('telegram_users')

            sample_dir = str(message.from_user.id)
            os.makedirs(sample_dir, exist_ok=True)
            os.chdir(sample_dir)

            os.makedirs(status_dict[user_id], exist_ok=True)
            os.chdir(status_dict[user_id])

            file_info = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            with open(f'{status_dict[user_id]}.png', 'wb') as new_file:
                new_file.write(downloaded_file)

            os.chdir(r"../")
            os.chdir(r"../")
            os.chdir(r"../")
            
            if status_dict[user_id] == 'style':         
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=1)        
                button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'styling'))
                button2 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
                markup.add(button1, button2)
                await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'saved_style'), reply_markup=markup)
                status_dict[user_id] = 'ready'
                sf.save_file(user_status_path, user_id, 'ready')

            if status_dict[user_id] == 'content':
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton(t.translate(language_dict[user_id], 'back'))
                markup.add(button1)
                await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'saved_content'), reply_markup=markup)
                status_dict[user_id] = 'style'
                sf.save_file(user_status_path, user_id, 'style')
        else:
            await bot.send_message(message.chat.id, t.translate(language_dict[user_id], 'press_button'))

    asyncio.run(bot.polling(none_stop=True, interval=2))
