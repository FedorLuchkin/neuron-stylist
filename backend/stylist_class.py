import gc
import torch
from torch import optim
import open_queue_file as of

class Stylist():
    
    def __init__(self, img, epochs, loss_layers, losses, weights, targets, normalize_image, vgg, user_id):
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
        result_list = list()      
        for i in range(0, self.epochs+1):
            loss = self.opt.step(self.step_opt)
            result_img = self.normalize_image(self.img[0]) 
            if i != 0 and i % 20 == 0:
                result_list.append(result_img)
            queue_dict = of.open_file()
            good_end = True
            if queue_dict[self.user_id] == -1:
                good_end = False
                print(self.user_id + ' canceled_in_fit')
                break
        gc.collect()
        torch.cuda.empty_cache()
        print('CUDA CACHE WAS CLEANED!')        
        return result_list, good_end