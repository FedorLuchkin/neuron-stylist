#!/usr/bin/env python
# coding: utf-8

# ## Основные функции

# ### Загрузка библиотек

# In[28]:


from IPython.display import clear_output
import gc
import matplotlib.pyplot as plt
import os
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch import optim
import torchvision
from torchvision import transforms


# ### Класс модели нейронной сети VGG16

# In[6]:


from pynvml import *
nvmlInit()
h = nvmlDeviceGetHandleByIndex(0)
info = nvmlDeviceGetMemoryInfo(h)
print(f'total    : {info.total / 1024 ** 2}')
print(f'free     : {info.free / 1024 ** 2}')
print(f'used     : {info.used / 1024 ** 2}')


# In[30]:


# архитектура нейронной сети VGG16
class VGG16(nn.Module):
    def __init__(self, pool='max'):
        super().__init__()
        self.conv1_1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.conv1_2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv2_1 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv2_2 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.conv3_1 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.conv3_2 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.conv3_3 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.conv3_4 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.conv4_1 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
        self.conv4_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv4_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv4_4 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv5_1 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv5_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv5_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv5_4 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        if pool == 'max':
            self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
            self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
            self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
            self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)
            self.pool5 = nn.MaxPool2d(kernel_size=2, stride=2)
        elif pool == 'avg':
            self.pool1 = nn.AvgPool2d(kernel_size=2, stride=2)
            self.pool2 = nn.AvgPool2d(kernel_size=2, stride=2)
            self.pool3 = nn.AvgPool2d(kernel_size=2, stride=2)
            self.pool4 = nn.AvgPool2d(kernel_size=2, stride=2)
            self.pool5 = nn.AvgPool2d(kernel_size=2, stride=2)
            
    def forward(self, x, layers):
        out = {}
        out['relu1_1'] = F.relu(self.conv1_1(x))
        out['relu1_2'] = F.relu(self.conv1_2(out['relu1_1']))
        out['pool1'] = self.pool1(out['relu1_2'])
        out['relu2_1'] = F.relu(self.conv2_1(out['pool1']))
        out['relu2_2'] = F.relu(self.conv2_2(out['relu2_1']))
        out['pool2'] = self.pool2(out['relu2_2'])
        out['relu3_1'] = F.relu(self.conv3_1(out['pool2']))
        out['relu3_2'] = F.relu(self.conv3_2(out['relu3_1']))
        out['relu3_3'] = F.relu(self.conv3_3(out['relu3_2']))
        out['relu3_4'] = F.relu(self.conv3_4(out['relu3_3']))
        out['pool3'] = self.pool3(out['relu3_4'])
        out['relu4_1'] = F.relu(self.conv4_1(out['pool3']))
        out['relu4_2'] = F.relu(self.conv4_2(out['relu4_1']))
        out['relu4_3'] = F.relu(self.conv4_3(out['relu4_2']))
        out['relu4_4'] = F.relu(self.conv4_4(out['relu4_3']))
        out['pool4'] = self.pool4(out['relu4_4'])
        out['relu5_1'] = F.relu(self.conv5_1(out['pool4']))
        out['relu5_2'] = F.relu(self.conv5_2(out['relu5_1']))
        out['relu5_3'] = F.relu(self.conv5_3(out['relu5_2']))
        out['relu5_4'] = F.relu(self.conv5_4(out['relu5_3']))
        out['pool5'] = self.pool5(out['relu5_4'])
        return [out[key] for key in layers]


# ### Классы для расчётов матриц Грама и ошибкок на их основе

# In[31]:


class GramMatrix(nn.Module):
    def forward(self, input):
        b,c,h,w = input.size()
        F = input.view(b, c, h*w)
        # torch.bmm: If input is a (b×n×m) tensor, mat2 is a (b×m×p) tensor, out will be a (b×n×p) tensor.
        G = torch.bmm(F, F.transpose(1,2)) # меняет местами 1 и 2 измерения
        G.div_(h*w)
        return G
class GramMSELoss(nn.Module):
    def forward(self, input, target):
        out = nn.MSELoss()(GramMatrix()(input), target) # MSE между матрицами Грама
        return out


# ### Класс для тренировки моделей

# In[32]:


class stylist():
    
    def __init__(self, img, epochs, loss_layers, losses, weights, targets, normalize_image, vgg):
        super().__init__()
        self.img = img
        self.opt = optim.LBFGS([self.img])
        self.epochs = epochs
        self.loss_layers = loss_layers
        self.losses = losses
        self.weights = weights
        self.targets = targets
        self.normalize_image = normalize_image
        self.vgg = vgg
        
    def step_opt(self):
        self.opt.zero_grad() # активируем оптимизатор
        out_layers = self.vgg(self.img, self.loss_layers) # получаем нужные слои модели
        layer_losses = []
        for j, out in enumerate(out_layers):
            layer_losses.append(self.weights[j] * self.losses[j](out, self.targets[j])) # подсчёт ошибки на слоях
        loss = sum(layer_losses) # суммированиме ошибок на слоях
        loss.backward() 
        return loss
    
    
    def fit(self):        
        for i in range(0, self.epochs+1):
            clear_output(wait=True)            
            loss = self.opt.step(self.step_opt)
            print('Epoch %d/%d | loss = %d' % (i, self.epochs, loss))
            result_img = self.normalize_image(self.img[0])
            #plt.imshow(result_img)
            #plt.axis('off')
            #plt.show()
        
        return result_img


# ### Функции для получения настроенных функций преобразований между изображениями и тензорами

# In[33]:


def img_functions(size, chanels):    
    to_mean_tensor = transforms.Compose([transforms.Resize(size), # иземенеие размера PIL изображения    
                               transforms.ToTensor(), # преобразование PIL изображения в тензор
                               transforms.Lambda(lambda x: x[torch.LongTensor(chanels)]), # в тензоре 3 канала, меняем 1 и 3 местами      
                               transforms.Normalize(mean=[0.40760392, 0.45795686, 0.48501961],   
                                                    std=[1,1,1]), # нормальзация тензора
                               transforms.Lambda(lambda x: x.mul_(255)), # деление на 255, чтобы значения были от 0 до 1 
                              ])

    to_unmean_tensor = transforms.Compose([transforms.Lambda(lambda x: x.div(255)),
                                            transforms.Normalize(mean=[-0.40760392, -0.45795686, -0.48501961],  
                                                    std=[1,1,1]),
                                            transforms.Lambda(lambda x: x[torch.LongTensor(chanels)]), 
                              ])
    to_image = transforms.Compose([transforms.ToPILImage()])
    normalize_image = lambda t: to_image(torch.clamp(to_unmean_tensor(t), min=0, max=1)) # на всякий случай, чтобы значения были от 0 до 1
    return(to_mean_tensor, normalize_image)


# ### Функция получения тензоров из входных изображений

# In[34]:


def get_img_tensors(imgs, to_mean_tensor):
    imgs_torch = [to_mean_tensor(img) for img in imgs]
    # Variable это надстройка над Tensor, которая позволяет подсчитывать градиенты для обратного распространения ошибки.
    # unsqueeze returns a new tensor with a dimension of size one inserted at the specified position.
    # require_grad указывает, является ли Variable обучаемой. 
    # По умолчанию require_grad имеет значение False при создании Variable.
    if torch.cuda.is_available():
        imgs_torch = [Variable(img.unsqueeze(0).cuda()) for img in imgs_torch]
    else:
        imgs_torch = [Variable(img.unsqueeze(0)) for img in imgs_torch]
    style_image, content_image = imgs_torch
    opt_img = Variable(content_image.data.clone(), requires_grad=True)
    return style_image, content_image, opt_img


# ### Функция получения параметров для обучения моделей

# In[35]:


def get_stylict_params(vgg, style_image, content_image):
    style_layers = ['relu1_1','relu2_1','relu3_1','relu4_1', 'relu5_1'] 
    content_layers = ['relu4_2']
    loss_layers = style_layers + content_layers
    losses = [GramMSELoss()] * len(style_layers) + [nn.MSELoss()] * len(content_layers) # список из 2 ф-й ошибок
    if torch.cuda.is_available():
        losses = [loss.cuda() for loss in losses]
    style_weights = [1e3/n**2 for n in [64,128,256,512,512]]
    content_weights = [1e0]
    weights = style_weights + content_weights # список из 2 списков весов для обучения
    style_targets = [GramMatrix()(A).detach() for A in vgg(style_image, style_layers)] # ответы для обучения стилю
    content_targets = [A.detach() for A in vgg(content_image, content_layers)] # ответы для обучения контенту
    targets = style_targets + content_targets # список из 2 списков ответов для обучения
    return loss_layers, losses, weights, targets


# ### Функция переноса стиля изображения

# In[36]:


def get_result(vgg, imgs, size = (1024, 1024), difference = 0, chanels = [0,1,2], epochs = 5):
    to_mean_tensor, normalize_image = img_functions(size, chanels)
    style_image, content_image, opt_img = get_img_tensors(imgs, to_mean_tensor)
    loss_layers, losses, weights, targets = get_stylict_params(vgg, style_image, content_image)
    model = stylist(opt_img, epochs, loss_layers, losses, weights, targets, normalize_image, vgg)
    result = model.fit()
    # освобождение видеопамяти
    model = None    
    gc.collect()
    torch.cuda.empty_cache()
    print('CUDA CACHE WAS CLEANED!')
    if difference != -1:
        return result.resize((size[1] + difference, size[0] + difference))
    else:
        return result.resize((size[1] * 2, size[0] * 2))


# ## Загрузка модели

# In[37]:


# загружаем веса модели VGG16, обученной на ImageNet
vgg_model  = VGG16()
vgg_model.load_state_dict(torch.load('vgg_conv.pth'))
# отключаем обучение, чтобы не испортить веса
for param in vgg_model.parameters():
    param.requires_grad = False
# как устройство для вычислений выбираем видеокарту
if torch.cuda.is_available():
    print('CUDA IS AVAILABLE :)')
    vgg_model.cuda()


# ## Загрузка изображений

# In[38]:


# загружаем картинки
os.chdir('style')
style_img = Image.open('style.png')
os.chdir(r"../")
os.chdir('content')
content_img = Image.open('content07.png')
os.chdir(r"../")
width, height = content_img.size
images = [style_img, content_img]


# In[39]:


print("Your size: {}x{}".format(width,height))
diff = 0
if width * height > 1024**2:
    print("Content image is too big!!!")
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
    print("New size: {}x{}".format(width,height))
    print("Size wil be return later")


# ## Преобразования

# In[41]:


# def get_result(SIZE_IMAGE = 1024, chanels = [0,1,2], epochs = 5)
SIZE_IMAGE = (height, width)
epoch_number = 20


# In[42]:


sample_dir = 'generated'
os.makedirs(sample_dir, exist_ok=True)


# In[43]:


result2 = get_result(vgg = vgg_model, imgs = images, size = SIZE_IMAGE, difference = diff, chanels = [2,1,0], epochs = epoch_number)


# In[41]:


os.chdir(sample_dir)
result2.save('result2.jpg')
os.chdir(r"../")


# In[19]:


result3 = get_result(vgg = vgg_model, imgs = images, size = SIZE_IMAGE, difference = diff, chanels = [0,2,1], epochs = epoch_number)


# In[20]:


os.chdir(sample_dir)
result3.save('result3.jpg')
os.chdir(r"../")


# In[8]:


#import numpy as np
#queue = {}
#np.save('queue.npy', queue) 


# In[ ]:




