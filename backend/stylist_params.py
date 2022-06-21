import gram as gr
import torch
import torch.nn as nn

def get_stylict_params(vgg, style_image, content_image):
    style_layers = ['relu1_1','relu2_1','relu3_1','relu4_1', 'relu5_1'] 
    content_layers = ['relu4_2']
    loss_layers = style_layers + content_layers
    losses = [gr.GramMSELoss()] * len(style_layers) + [nn.MSELoss()] * len(content_layers) # список из 2 ф-й ошибок
    if torch.cuda.is_available():
        losses = [loss.cuda() for loss in losses]
    style_weights = [1e3/n**2 for n in [64,128,256,512,512]]
    content_weights = [1e0]
    weights = style_weights + content_weights # список из 2 списков весов для обучения
    style_targets = [gr.GramMatrix()(A).detach() for A in vgg(style_image, style_layers)] # ответы для обучения стилю
    content_targets = [A.detach() for A in vgg(content_image, content_layers)] # ответы для обучения контенту
    targets = style_targets + content_targets # список из 2 списков ответов для обучения
    return loss_layers, losses, weights, targets
    