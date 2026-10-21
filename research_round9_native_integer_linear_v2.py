"""Integer-forward linear surrogate with correctly rounded FP32 divisions.

FP32 CUDA division by a constant can become reciprocal multiplication. Native
AVX uses IEEE division. Computing the ratio in FP64 before casting to FP32
preserves the native single-precision quotient for these finite quantizers.
"""
import types
import torch
from torch.nn import functional as F

def div32(x,s):return (x.double()/torch.as_tensor(s,device=x.device).double()).float()

def install(model):
 sites=[]
 for name,module in model.named_modules():
  if module.__class__.__name__ in ['DynamicAct','StaticAct']:
   dynamic=module.__class__.__name__=='DynamicAct'
   def act(self,x,_dynamic=dynamic,**kwargs):
    scale=div32(x.abs().amax(-1,keepdim=True).clamp_min(1e-12),127.) if _dynamic else self.scale
    q=torch.round(div32(x,scale)).clamp(-128,127)*scale
    return q.detach()+(x-x.detach())
   module.forward=types.MethodType(act,module)
  if not hasattr(module,'quantize_activation') or module.quantize_activation is None or not hasattr(module,'quantize_weight') or module.quantize_weight is None:continue
  def forward(self,x,initialize_scales):
   qx=self.quantize_activation(x,initialize_scales_steps=initialize_scales.activation_steps,return_ints=False);qw=self.quantize_weight(self.weight,initialize_scales_steps=initialize_scales.weight_steps,return_ints=False);surrogate=F.linear(qx,qw)
   with torch.no_grad():
    sa=div32(x.abs().amax(-1,keepdim=True).clamp_min(1e-12),127.)
    ai=torch.round(div32(x,sa)).clamp(-128,127)
    wq=self.quantize_weight;fold=wq.scale*wq.grid;wi=torch.round(div32(qw,fold));dots=F.linear(ai,wi)
    native=(dots*fold.reshape(-1))*sa
    if self.bias is not None:native=native+self.bias
   if self.bias is not None:surrogate=surrogate+self.bias
   return native.detach()+(surrogate-surrogate.detach())
  module.forward=types.MethodType(forward,module);sites.append(name)
 return sites
