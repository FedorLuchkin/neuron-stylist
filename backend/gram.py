import torch
import torch.nn as nn


class GramMatrix(nn.Module):

    def forward(self, input):
        batch, channel, height, width = input.size()
        input = input.view(batch, channel, height * width)
        matrix = torch.bmm(input, input.transpose(1, 2))
        matrix.div_(height * width)
        return matrix


class GramMSELoss(nn.Module):
    
    def forward(self, input, target):
        output = nn.MSELoss()(GramMatrix()(input), target)
        return output
