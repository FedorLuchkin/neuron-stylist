import asyncio
import numpy as np
import os
import shutil
import sys
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import subprocess
import path_editor
from backend import open_queue_file as of

if len(sys.argv) != 2:
    print('one argument (token) expected')
else:
    print('bot was started')

    token = sys.argv[1]
    img_num = 3

    if os.path.exists('frontend/users_status.npy'):        
        status_dict = np.load('frontend/users_status.npy', allow_pickle=True).item()
    else:        
        status_dict = dict()
        np.save('frontend/users_status.npy', status_dict)
        print('status_dict was created')
    empty_dict = dict()
    np.save('backend/queue.npy', empty_dict)
    print('queue_dict was created')

    bot = AsyncTeleBot(token)

    examples = '''
Image conversion examples: 
https://disk.yandex.ru/d/--ASEOmS5QfUuA

Video conversion examples (this feature will be added to the bot soon):
https://youtube.com/playlist?list=PL5MVMi3Spz2t7aC1cP4FLyjTB6vfOkUCv
    '''
    async def result_waiting(message):
        global bot
        global examples
        global instructions
        global status_dict
        global img_num
        user_id = str(message.from_user.id)
        result_path = 'telegram_users/' + user_id + '/result/result' + str(img_num - 1) +'.png'
        result_status = False
        while not result_status and status_dict[user_id] == 'processing':
            result_status = os.path.exists(result_path)
            await asyncio.sleep(5)

        if result_status and status_dict[user_id] == 'processing':
                status_dict[user_id] = 'done'
                np.save('frontend/users_status.npy', status_dict) 
                photo_list = list()
                for i in range(0, img_num):
                    result_path = 'telegram_users/' + str(message.from_user.id) + '/result/result' + str(i) +'.png'
                    photo = telebot.types.InputMediaPhoto(open(result_path, 'rb'))
                    photo_list.append(photo) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button1 = types.KeyboardButton('Back to START ↩️↩️')
                markup.add(button1)
                await bot.send_media_group(message.chat.id, photo_list)
                await bot.send_message(message.chat.id, 'Ready!', reply_markup=markup)
                del_path = 'telegram_users/' + str(message.from_user.id)
                if os.path.exists(del_path):
                    shutil.rmtree(del_path, ignore_errors=True)

        

    @bot.message_handler(commands='start')
    async def start(message):
        global status_dict
        user_id = str(message.from_user.id)
        status_dict[user_id] = 'beginning'
        np.save('frontend/users_status.npy', status_dict)        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton('START')
        button2 = types.KeyboardButton('examples of stylist work')
        markup.add(button1, button2)    
        await bot.send_message(message.chat.id, "Let's start!", reply_markup=markup)


    @bot.message_handler(content_types=['text'])
    async def get_user_text(message):       
        global examples
        global instructions
        global status_dict
        global img_num
        user_id = str(message.from_user.id)
        
        if message.text == 'statuses' and message.chat.id == 'ADMIN_ID':
            await bot.send_message(message.chat.id, str(status_dict))

        elif message.text == 'queue' and message.chat.id == 'ADMIN_ID':
            if os.path.exists('backend/queue.npy'):
                queue_dict = of.open_file()
                await bot.send_message(message.chat.id, str(queue_dict))

        elif status_dict[user_id] == 'content' or status_dict[user_id] == 'style':
            if message.text != 'Back ↩️':        
                await bot.send_message(message.chat.id, 'This is not an image')
                
        elif message.text == 'examples of stylist work':
            await bot.send_message(message.chat.id, examples)
            
        elif message.text == 'START':
            status_dict[user_id] = 'content' 
            np.save('frontend/users_status.npy', status_dict)        
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button1 = types.KeyboardButton('Back ↩️')
            markup.add(button1)        
            await bot.send_message(message.chat.id, 'Send the image you want to change', reply_markup=markup)        
            
        elif message.text == '🟢 STYLING 🟢': 
            del_path = 'telegram_users/' + user_id + '/result'
            if os.path.exists(del_path):
                shutil.rmtree(del_path, ignore_errors=True)
            content_path = 'telegram_users/' + str(message.from_user.id) + '/content/content.png'
            style_path = 'telegram_users/' + str(message.from_user.id) + '/style/style.png'
            content_status = os.path.exists(content_path)
            style_status = os.path.exists(style_path)
            if not (content_status and style_status):
                if not content_status:
                    await bot.send_message(message.chat.id, 'Content image not found!')
                if not style_status:
                    await bot.send_message(message.chat.id, 'Style image not found!')
            else:
                queue_dict = of.open_file()
                if len(queue_dict) == 0:
                    queue_dict[user_id] = 1
                    np.save('backend/queue.npy', queue_dict)
                else:
                    queue_dict[user_id] = 0
                    np.save('backend/queue.npy', queue_dict)
                
                subprocess.Popen(["python", "backend/neuron_stylist.py", user_id])

                status_dict[user_id] = 'processing'
                np.save('frontend/users_status.npy', status_dict) 

                future = asyncio.ensure_future(result_waiting(message))

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                button1 = types.KeyboardButton('cancel styling ❌')
                markup.add(button1)
                await bot.send_message(message.chat.id, 'Styling was started. This will take some time...', reply_markup=markup)
        
        elif message.text == 'cancel styling ❌' and status_dict[user_id] == 'processing':
            queue_dict = of.open_file()
            if len(queue_dict) > 0 and user_id in queue_dict.keys():
                queue_dict[user_id] = -1
                np.save('backend/queue.npy', queue_dict)

            status_dict[user_id] = 'ready'
            np.save('frontend/users_status.npy', status_dict) 
            del_path = 'telegram_users/' + user_id + '/result'
            if os.path.exists(del_path):
                shutil.rmtree(del_path, ignore_errors=True)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)        
            button1 = types.KeyboardButton('🟢 STYLING 🟢')
            button2 = types.KeyboardButton('Back ↩️')
            markup.add(button1, button2)
            await bot.send_message(message.chat.id, 'We can start styling', reply_markup=markup)

        elif message.text == 'Back to START ↩️↩️':
            status_dict[user_id] = 'beginning'
            np.save('frontend/users_status.npy', status_dict) 
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button1 = types.KeyboardButton('START')
            button2 = types.KeyboardButton('examples of stylist work')
            markup.add(button1, button2)    
            await bot.send_message(message.chat.id, "Let's start!", reply_markup=markup)    
            
        elif message.text != 'Back ↩️':
            await bot.send_message(message.chat.id, 'unknown command')
            
        if message.text == 'Back ↩️':
            if status_dict[user_id] == 'ready':
                status_dict[user_id] = 'style'
                np.save('frontend/users_status.npy', status_dict) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton('Back ↩️')
                markup.add(button1)
                await bot.send_message(message.chat.id, 'Send style image', reply_markup=markup)
            elif status_dict[user_id] == 'style':
                status_dict[user_id] = 'content'
                np.save('frontend/users_status.npy', status_dict) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton('Back ↩️')
                markup.add(button1)
                await bot.send_message(message.chat.id, 'Send the image you want to change', reply_markup=markup)
            elif status_dict[user_id] == 'content':
                status_dict[user_id] = 'beginning'
                np.save('frontend/users_status.npy', status_dict) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton('START')
                button2 = types.KeyboardButton('examples of stylist work')
                markup.add(button1, button2)
                await bot.send_message(message.chat.id, "Let's start!", reply_markup=markup)


    @bot.message_handler(content_types=['photo'])
    async def get_user_photo(message):
        global status_dict
        user_id = str(message.from_user.id)
        
        if status_dict[user_id] == 'content' or status_dict[user_id] == 'style':
            os.makedirs('telegram_users', exist_ok=True)
            os.chdir('telegram_users')

            sample_dir = str(message.from_user.id)
            os.makedirs(sample_dir, exist_ok=True)
            os.chdir(sample_dir)

            os.makedirs(status_dict[user_id], exist_ok=True)
            os.chdir(status_dict[user_id])

            file_info = await bot.get_file(message.photo[len(message.photo)-1].file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            with open(f'{status_dict[user_id]}.png', 'wb') as new_file:
                new_file.write(downloaded_file)

            os.chdir(r"../")
            os.chdir(r"../")
            os.chdir(r"../")
            
            if status_dict[user_id] == 'style':
                status_dict[user_id] = 'ready'
                np.save('frontend/users_status.npy', status_dict) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)        
                button1 = types.KeyboardButton('🟢 STYLING 🟢')
                button2 = types.KeyboardButton('Back ↩️')
                markup.add(button1, button2)
                await bot.send_message(message.chat.id, 'Your style image was received, now we can start styling', reply_markup=markup)

            if status_dict[user_id] == 'content':
                status_dict[user_id] = 'style'
                np.save('frontend/users_status.npy', status_dict) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton('Back ↩️')
                markup.add(button1)
                await bot.send_message(message.chat.id, 'Your image was received, now send style image', reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, 'You submitted an image but a button click was expected')

    asyncio.run(bot.polling(none_stop=True))
