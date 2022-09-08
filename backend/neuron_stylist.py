import gc
import numpy as np
import os
from PIL import Image
import stylist_result as sr
import sys
import time
import torch
from vgg import VGG16
import open_queue_file as of
import path_editor
from datetime import datetime


if len(sys.argv) != 2:
    print('one argument expected')
else:
    user_id = sys.argv[1]

    queue_dict = of.open_file()
    if queue_dict[user_id] == 0:
        print(user_id + ' are waiting ' + str(datetime.now()))

    while queue_dict[user_id] == 0:
        queue_dict = of.open_file()
        time.sleep(2)

    if queue_dict[user_id] == -1:
        print(user_id + ' canceled_before_start ' + str(datetime.now()))
        queue_dict = of.open_file()
        if user_id in queue_dict.keys():
            del queue_dict[user_id]
            np.save('backend/queue.npy', queue_dict)

    elif queue_dict[user_id] == 1:
        print(user_id + ' started ' + str(datetime.now()))

        vgg_model = VGG16()
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
        # chanels = [2,1,0]
        result, good_end = sr.get_result(
            vgg=vgg_model, imgs=images, size=SIZE_IMAGE, difference=diff, chanels=[
                0,2,1], epochs=epoch_number, user=user_id)
        if good_end:
            result_path = 'telegram_users/' + user_id + '/result'
            os.makedirs(result_path, exist_ok=True)
            for i in range(0, len(result)):
                result_path = 'telegram_users/' + user_id + \
                    '/result/result' + str(i) +'.png'
                result[i].save(result_path)
        print(user_id + ' styling time ' + str(datetime.now() - start_time))

        gc.collect()
        torch.cuda.empty_cache()

        queue_dict = of.open_file()
        if user_id in queue_dict.keys():
            del queue_dict[user_id]
            np.save('backend/queue.npy', queue_dict)

        queue_dict = of.open_file()
        if len(queue_dict) > 0:
            key = list(queue_dict.keys())[0]
            if queue_dict[key] == 0:
                queue_dict[key] = 1
        np.save('backend/queue.npy', queue_dict)

    print(user_id + ' finished ' + str(datetime.now()))
