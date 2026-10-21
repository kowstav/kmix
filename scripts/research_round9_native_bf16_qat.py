"""STE for original BF16 parameters, preserving native storage semantics.

Patch only reads of actual original BF16 parameter attributes in each owning
module forward. No parameter renaming or additional checkpoint buffers. Fail
explicitly if a required forward cannot be patched; never silently skip it.
"""
import ast,inspect,textwrap,types
import torch
def bf16_ste(x):return x+(x.to(torch.bfloat16).to(x.dtype)-x).detach()
def install(model,original_entries):
 params=dict(model.named_parameters());by_parent={}
 for name,(dtype,array) in original_entries.items():
  if dtype!=1 or name not in params:continue
  parent,_,attribute=name.rpartition('.');by_parent.setdefault(parent,set()).add(attribute)
 sites=[]
 for parent,attributes in by_parent.items():
  module=model.get_submodule(parent) if parent else model;old=module.forward;source=textwrap.dedent(inspect.getsource(inspect.unwrap(old)));tree=ast.parse(source);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef));function.decorator_list=[];found=set()
  if any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='super' for n in ast.walk(function)):raise RuntimeError('cannot recompile super closure '+parent)
  class Rewriter(ast.NodeTransformer):
   def visit_Attribute(self,node):
    if isinstance(node.ctx,ast.Load) and isinstance(node.value,ast.Name) and node.value.id=='self' and node.attr in attributes:
     found.add(node.attr);return ast.copy_location(ast.Call(func=ast.Name(id='__hp_native_bf16_ste',ctx=ast.Load()),args=[node],keywords=[]),node)
    return self.generic_visit(node)
  function=Rewriter().visit(function);assert found==attributes,(parent,attributes,found);ast.fix_missing_locations(function);ns=dict(inspect.unwrap(old).__globals__);ns['__hp_native_bf16_ste']=bf16_ste;exec(compile(ast.Module(body=[function],type_ignores=[]),'<original-bf16-parameter-forward>','exec'),ns);module.forward=types.MethodType(ns[function.name],module);sites.extend((parent+'.'+a).strip('.') for a in sorted(attributes))
 assert set(sites)=={name for name,(dt,a) in original_entries.items() if dt==1 and name in params};return sites
