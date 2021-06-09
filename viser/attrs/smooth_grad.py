import torch
import torch.nn as nn

__all__ = ['SmoothGrad']

class SmoothGrad:
    def __init__(self, model: nn.Module) -> None:
        model.eval()
        self.model = model
    
    def attribute(self, input: torch.Tensor, target: int = None, epochs: int=50, abs: bool = True):
        assert input.dim() == 4, ''
        
        grad = torch.zeros(input.shape)

        for i in range(epochs):
            noise = torch.randn(input.shape) / 5
            x = input.detach().clone()
            
            x += noise
            
            if not x.requires_grad:
                x.requires_grad_()
                
            if x.grad is not None:
                x.grad.zero_()
                
            output = self.model(x)
            # loss = torch.sum(output, 1)
            loss = output[0, target] if target and target < output.shape[1] else output.max()
            
            grad += torch.autograd.grad(loss, x)[0]
        
        return torch.abs(grad / epochs) if abs else (grad / epochs)