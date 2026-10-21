"""Native AVX2 single-chain eight-lane RMS forward, usual RMS gradient."""
import torch
from torch.nn import functional as F
from research_round9_native_integer_linear_v2 import div32

def rms_norm(x):
 surrogate=F.rms_norm(x,normalized_shape=(x.size(-1),))
 with torch.no_grad():
  n=x.shape[-1];assert n%8==0
  lanes=torch.zeros(x.shape[:-1]+(8,),device=x.device,dtype=torch.float32)
  for i in range(0,n,8):
   v=x[...,i:i+8].double();lanes=(v*v+lanes.double()).float()
  s=lanes[...,:4]+lanes[...,4:]
  a=s[...,0]+s[...,2];b=s[...,1]+s[...,3];total=a+b
  ms=div32(total,float(n));epsilon=torch.finfo(torch.float32).eps
  denom=((ms+epsilon).double().sqrt()).float()[...,None]
  result=div32(x,denom)
 return result.detach()+(surrogate-surrogate.detach())
