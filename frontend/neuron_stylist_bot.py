import asyncio
import numpy as np
import os
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
        #await bot.send_message(message.chat.id, str(status_dict))


    @bot.message_handler(content_types=['text'])
    async def get_user_text(message):       
        global examples
        global instructions
        global status_dict
        user_id = str(message.from_user.id)
        
        if message.text == 'get statuses' and message.chat.id == 234764423:
            await bot.send_message(message.chat.id, str(status_dict))
        
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
            await bot.send_message(message.chat.id, 'Send a image you want to change', reply_markup=markup)        
            
        elif message.text == '🟢 STYLING 🟢': 
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
                
                subprocess.Popen(["python", "backend/test_sub.py", user_id])

                status_dict[user_id] = 'processing'
                np.save('frontend/users_status.npy', status_dict) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                button1 = types.KeyboardButton('Is my picture ready?')
                button2 = types.KeyboardButton('cancel styling ❌')
                markup.add(button1, button2)
                await bot.send_message(message.chat.id, 'Styling was started. This will take some time...', reply_markup=markup)
        
        elif message.text == 'cancel styling ❌' and status_dict[user_id] == 'processing':
            queue_dict = of.open_file()
            if len(queue_dict) > 0 and user_id in queue_dict.keys():
                queue_dict[user_id] = -1
                np.save('backend/queue.npy', queue_dict)

            status_dict[user_id] = 'ready'
            np.save('frontend/users_status.npy', status_dict) 
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)        
            button1 = types.KeyboardButton('🟢 STYLING 🟢')
            button2 = types.KeyboardButton('Back ↩️')
            markup.add(button1, button2)
            await bot.send_message(message.chat.id, 'We can start styling', reply_markup=markup) 

        elif message.text == 'Is my picture ready?':
            result_path = 'telegram_users/' + str(message.from_user.id) + '/result/result.png'
            result_status = os.path.exists(result_path)
            if result_status:
                status_dict[user_id] = 'done'
                np.save('frontend/users_status.npy', status_dict) 
                photo = open(result_path, 'rb')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                button1 = types.KeyboardButton('Back ↩️')
                button2 = types.KeyboardButton('Back to START ↩️↩️')
                markup.add(button1, button2)
                await bot.send_photo(message.chat.id, photo)
                await bot.send_message(message.chat.id, 'Ready!', reply_markup=markup)
            else:
                await bot.send_message(message.chat.id, 'Result not ready... Please wait')

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
            if status_dict[user_id] == 'done':
                status_dict[user_id] = 'ready'
                np.save('frontend/users_status.npy', status_dict) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)        
                button1 = types.KeyboardButton('🟢 STYLING 🟢')
                button2 = types.KeyboardButton('Back ↩️')
                markup.add(button1, button2)
                await bot.send_message(message.chat.id, 'We can start styling', reply_markup=markup)
            elif status_dict[user_id] == 'ready':
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
                await bot.send_message(message.chat.id, 'Send a image you want to change', reply_markup=markup)
            elif status_dict[user_id] == 'content':
                status_dict[user_id] = 'beginning'
                np.save('frontend/users_status.npy', status_dict) 
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                button1 = types.KeyboardButton('START')
                button2 = types.KeyboardButton('examples of stylist work')
                markup.add(button1, button2)
                await bot.send_message(message.chat.id, "Let's start!", reply_markup=markup)
        #await bot.send_message(message.chat.id, str(status_dict))      


    @bot.message_handler(content_types=['photo'])
    async def get_user_photo(message):
        #global status
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
        #await bot.send_message(message.chat.id, str(status_dict))

    asyncio.run(bot.polling(none_stop=True))