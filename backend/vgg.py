import torch.nn as nn
import torch.nn.functional as F


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
