from datetime import datetime
import gc
import logging
import os
import path_editor
from PIL import Image
import secure_file_open as of
import secure_file_save as sf
import stylist_result as sr
import sys
import time
import torch
from vgg import VGG19

queue_path = 'backend/queue.npy'
logging.basicConfig(filename='sessions.log', encoding='utf-8', level=logging.DEBUG)

if len(sys.argv) != 2:
    logging.error({'type': 'nst_starting', 'data': 'one argument (user_id) expected'})
else:
    user_id = sys.argv[1]

    queue_dict = of.open_file(queue_path)
    if queue_dict[user_id] == 0:
        logging.info({'type': 'user_status', 'data': {'user_id': user_id, 'status': 'waiting', 'time': str(datetime.now())}})

    while queue_dict[user_id] == 0:
        queue_dict = of.open_file(queue_path)
        time.sleep(2)

    if queue_dict[user_id] == -1:
        logging.info({'type': 'user_status', 'data': {'user_id': user_id, 'status': 'canceled_before_start', 'time': str(datetime.now())}})
        queue_dict = of.open_file(queue_path)
        if user_id in queue_dict.keys():
            sf.save_file(queue_path, user_id, -1, delete=True)

    elif queue_dict[user_id] == 1:
        logging.info({'type': 'user_status', 'data': {'user_id': user_id, 'status': 'started', 'time': str(datetime.now())}})

        vgg_model = VGG19()
        vgg_model.load_state_dict(torch.load('backend/vgg_conv.pth'))

        for param in vgg_model.parameters():
            param.requires_grad = False

        if torch.cuda.is_available():
            vgg_model.cuda()

        content_path = 'telegram_users/' + user_id + '/content/content.png'
        style_path = 'telegram_users/' + user_id + '/style/style.png'

        style_img = Image.open(style_path)
        content_img = Image.open(content_path)
        width, height = content_img.size
        images = [style_img, content_img]

        diff = 0
        if width * height > 1024**2:
            if width * height <= 2048**2:
                diff = -1
                width = int(width / 2)
                height = int(height / 2)

            else:
                if width > height:
                    diff = width - 1024
                else:
                    diff = height - 1024
                width -= diff
                height -= diff

        SIZE_IMAGE = (height, width)
        epoch_number = 60

        start_time = datetime.now()
        result, good_end = sr.get_result(
            vgg=vgg_model, 
            imgs=images, 
            size=SIZE_IMAGE, 
            difference=diff, 
            chanels=[
                    2,
                    1,
                    0], 
            epochs=epoch_number, 
            user=user_id)
        if good_end:
            result_path = 'telegram_users/' + user_id + '/result'
            os.makedirs(result_path, exist_ok=True)
            for i in range(0, len(result)):
                result_path = 'telegram_users/' + user_id + \
                    '/result/result' + str(i) +'.png'
                result[i].save(result_path)
        logging.info({'type': 'user_status', 'data': {'user_id': user_id, 'status': 'result_time', 'time': str(datetime.now() - start_time)}})

        gc.collect()
        torch.cuda.empty_cache()

        queue_dict = of.open_file(queue_path)
        if user_id in queue_dict.keys():
            sf.save_file(queue_path, user_id, -1, delete=True)

        queue_dict = of.open_file(queue_path)
        if len(queue_dict) > 0:
            key = list(queue_dict.keys())[0]
            if queue_dict[key] == 0:
                queue_dict[key] = 1
                sf.save_file(queue_path, key, 1)
    logging.info({'type': 'user_status', 'data': {'user_id': user_id, 'status': 'finished', 'time': str(datetime.now())}})
