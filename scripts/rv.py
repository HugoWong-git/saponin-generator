import torch, sys, types, importlib.abc, importlib.machinery

class Dummy:
    def __init__(self,*a,**k): pass
    def __setstate__(self,s):
        if isinstance(s,dict): self.__dict__.update(s)
        else: self.__dict__['_state']=s

class FakeMod(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"): raise AttributeError(name)
        cls=type(name,(Dummy,),{}); setattr(self,name,cls); return cls

class Loader(importlib.abc.Loader):
    def create_module(self, spec): return FakeMod(spec.name)
    def exec_module(self, module): pass

class Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0]=="reinvent":
            return importlib.machinery.ModuleSpec(fullname, Loader(), is_package=True)
        return None

sys.meta_path.insert(0, Finder())

def load(p):
    return torch.load(p, map_location="cpu", weights_only=False)
