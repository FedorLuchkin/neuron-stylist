from datetime import datetime
import gc
import img_functions as imf
import logging
from PIL import Image
import secure_file_open as of
import secure_file_save as sf
import stylist_params as sp
import torch
from torch import optim

logging.basicConfig(filename='sessions.log', encoding='utf-8', level=logging.DEBUG)
class Stylist():
    EPOCH = 0
    def __init__(self, img, epochs, loss_layers, losses, weights, targets, normalize_image, vgg, user_id, img_size):
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
        self.user_id = user_id
        self.img_size = img_size
        
    def step_opt(self):
        self.opt.zero_grad()
        out_layers = self.vgg(self.img, self.loss_layers)
        layer_losses = []
        for j, out in enumerate(out_layers):
            layer_losses.append(self.weights[j] * self.losses[j](out, self.targets[j]))
        loss = sum(layer_losses)
        loss.backward()
        return loss    
    
    def fit(self):  
        fit_progress_path = 'backend/fit_progress.npy'
        result_list = list()      
        for i in range(0, self.epochs+1):
            loss = self.opt.step(self.step_opt)
            self.EPOCH = self.EPOCH + 1
            result_img = self.normalize_image(self.img[0]) 
            if i != 0 and (i % 20 == 0 or i == 5):
                result_list.append(result_img)
            queue_dict = of.open_file('backend/queue.npy')
            good_end = True
            if queue_dict[self.user_id] == -1:
                good_end = False
                logging.info({'type': 'user_status', 'data': {'user_id': self.user_id, 'status': 'canceled_in_fit', 'time': str(datetime.now())}})
                break
            sf.save_file(fit_progress_path, self.user_id, round(i / self.epochs * 100, 1))

            # styling mode changing
            if self.EPOCH == 5:
                style_path = 'telegram_users/' + self.user_id + '/style/style.png'
                style_img = Image.open(style_path)
                content_img = self.normalize_image(self.img[0])
                chanels = [0, 2, 1]
                to_mean_tensor, self.normalize_image = imf.get_img_functions(self.img_size, chanels)
                style_image, content_image, self.img = imf.get_img_tensors([style_img, content_img], to_mean_tensor)
                self.opt = optim.LBFGS([self.img])
                loss_layers, losses, self.weights, self.targets = sp.get_stylict_params(
                    self.vgg, style_image, content_image, style_degree=3)
            
        sf.save_file(fit_progress_path, self.user_id, -1, delete=True)
        gc.collect()
        torch.cuda.empty_cache()
        return result_list, good_end
