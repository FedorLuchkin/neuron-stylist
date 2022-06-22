import gc
import torch
from stylist_class import Stylist
import stylist_params as sp
import img_functions as imf

def get_result(user, vgg, imgs, size = (1024, 1024), difference = 0, chanels = [0,1,2], epochs = 5):
    to_mean_tensor, normalize_image = imf.get_img_functions(size, chanels)
    style_image, content_image, opt_img = imf.get_img_tensors(imgs, to_mean_tensor)
    loss_layers, losses, weights, targets = sp.get_stylict_params(vgg, style_image, content_image)
    model = Stylist(opt_img, epochs, loss_layers, losses, weights, targets, normalize_image, vgg, user)
    result_list, good_end = model.fit()
    model = None    
    gc.collect()
    torch.cuda.empty_cache()
    print('CUDA CACHE WAS CLEANED!')
    for el in result_list:
            if difference != -1:
                el = el.resize((size[1] + difference, size[0] + difference))
            else:
                el = el.resize((size[1] * 2, size[0] * 2))
    return result_list, good_end
