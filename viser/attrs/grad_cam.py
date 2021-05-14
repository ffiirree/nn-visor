import torch
import torch.nn as nn
from torch import Tensor
from torch.nn import Module
from torch.nn.modules import activation
from viser.hooks import LayerForwardHook

__all__ = ['GradCAM']

class GradCAM:
    def __init__(self, model: Module, layer_index: int) -> None:
        self.model = model
        self.layer_index = layer_index
        self.forward_hook = LayerForwardHook(self.model, self.layer_index)
        
        self.model.eval()
            
    def attribute(self, input: Tensor, target: int = None, relu_attributions: bool = False):
        assert input.dim() == 4, ""
        
        if not input.requires_grad:
            input.requires_grad_()
            
        if input.grad is not None:
            input.grad.zero_()

        output = self.model(input)
        loss = output[0, target] if target else output.max()
        
        activations = self.forward_hook.activations
        gradients = torch.autograd.grad(loss, activations)[0]
        
        summed_grads = torch.mean(gradients, (2, 3), keepdim=True)
        scaled_activations = torch.sum(summed_grads * activations, dim=1, keepdim=True)
        
        return scaled_activations if not relu_attributions else torch.relu(relu_attributions)