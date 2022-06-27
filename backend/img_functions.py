import torch
from torchvision import transforms
from torch.autograd import Variable


def get_img_functions(size, chanels):    
    to_mean_tensor = transforms.Compose([transforms.Resize(size),   
                                         transforms.ToTensor(),
                                         transforms.Lambda(lambda x: x[torch.LongTensor(chanels)]),     
                                         transforms.Normalize(mean=[0.40760392, 0.45795686, 0.48501961],   
                                                              std=[1, 1, 1]),
                                         transforms.Lambda(lambda x: x.mul_(255)),
                                         ])

    to_unmean_tensor = transforms.Compose([transforms.Lambda(lambda x: x.div(255)),
                                           transforms.Normalize(mean=[-0.40760392, -0.45795686, -0.48501961],  
                                                                std=[1,1,1]),
                                           transforms.Lambda(lambda x: x[torch.LongTensor(chanels)]), 
                                           ])
    to_image = transforms.Compose([transforms.ToPILImage()])
    def normalize_image(t): return to_image(
        torch.clamp(to_unmean_tensor(t), min=0, max=1))
    return(to_mean_tensor, normalize_image)



def get_img_tensors(imgs, to_mean_tensor):
    imgs_torch = [to_mean_tensor(img) for img in imgs]
    if torch.cuda.is_available():
        imgs_torch = [Variable(img.unsqueeze(0).cuda()) for img in imgs_torch]
    else:
        imgs_torch = [Variable(img.unsqueeze(0)) for img in imgs_torch]
    style_image, content_image = imgs_torch
    opt_img = Variable(content_image.data.clone(), requires_grad=True)
    return style_image, content_image, opt_img

