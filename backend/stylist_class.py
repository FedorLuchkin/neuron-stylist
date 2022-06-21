from torch import optim

class Stylist():
    
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
            loss = self.opt.step(self.step_opt)
            result_img = self.normalize_image(self.img[0])        
        return result_img