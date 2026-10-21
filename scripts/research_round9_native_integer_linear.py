"""Native integer-forward surrogate with a separate fake-quant STE gradient.

Integer-valued FP32 GEMM is exact while all partial sums stay below2^24. Native
sites have bounded products/sums below that threshold. TF32 must be disabled.
"""
import types
import torch
from torch.nn import functional as F
def install(model):
 sites=[]
 for name,module in model.named_modules():
  if not hasattr(module,'quantize_activation') or module.quantize_activation is None or not hasattr(module,'quantize_weight') or module.quantize_weight is None:continue
  def forward(self,x,initialize_scales):
   # Preserve the original surrogate derivative through the quantizers.
   qx=self.quantize_activation(x,initialize_scales_steps=initialize_scales.activation_steps,return_ints=False);qw=self.quantize_weight(self.weight,initialize_scales_steps=initialize_scales.weight_steps,return_ints=False);surrogate=F.linear(qx,qw)
   with torch.no_grad():
    sa=x.abs().amax(-1,keepdim=True).clamp_min(1e-12)/127.;ai=torch.round(x/sa).clamp(-128,127);wq=self.quantize_weight;fold=wq.scale*wq.grid;wi=torch.round(qw/fold);dots=F.linear(ai,wi)
    native=(dots*fold.reshape(-1))*sa
    if self.bias is not None:native=native+self.bias
   if self.bias is not None:surrogate=surrogate+self.bias
   return surrogate+(native-surrogate).detach()
  module.forward=types.MethodType(forward,module);sites.append(name)
 return sites
