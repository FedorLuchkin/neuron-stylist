import os
from PIL import Image
import stylist_result as sr
import torch
from vgg import VGG16
import path_editor

vgg_model  = VGG16()
vgg_model.load_state_dict(torch.load('backend/vgg_conv.pth'))

for param in vgg_model.parameters():
    param.requires_grad = False

if torch.cuda.is_available():    
    vgg_model.cuda()

user_id = 'lol'

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


# get_result(vgg, imgs, size = (1024, 1024), difference = 0, chanels = [0,1,2], epochs = 5)
SIZE_IMAGE = (height, width)
epoch_number = 20

result_path = 'telegram_users/' + user_id + '/result'
os.makedirs(result_path, exist_ok=True)

result2 = sr.get_result(vgg = vgg_model, imgs = images, size = SIZE_IMAGE, difference = diff, chanels = [2,1,0], epochs = epoch_number)

result_path = 'telegram_users/' + user_id + '/result/result.png'

result2.save(result_path)

#result3 = sr.get_result(vgg = vgg_model, imgs = images, size = SIZE_IMAGE, difference = diff, chanels = [0,2,1], epochs = epoch_number)

#os.chdir(sample_dir)
#result3.save('result3.jpg')
#os.chdir(r"../")