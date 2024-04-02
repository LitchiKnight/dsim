import os
from config.env import Env
from common.utils import Utils
from common.const import *

class BaseCmd:
  def __init__(self, args: tuple) -> None:
    self.args = args
    self.proj = Env.get_proj(args.project)

  def get_module_path(self, module: str) -> str:
    return os.path.join(self.proj.TB_PATH, module)
  
  def get_list_path(self, module: str, _list: str) -> str:
    return os.path.join(self.proj.TB_PATH, module, TC_LST_DIR, _list)

  def has_project(self) -> bool:
    return os.path.exists(self.proj.WORK_PATH)
  
  def has_module(self, module: str) -> bool:
    return os.path.exists(self.get_module_path(module))
  
  def has_list(self, module: str, _list: str) -> bool:
    return os.path.exists(self.get_list_path(module, _list))
  
  def fetch_modules(self) -> list:
    return [f.name for f in os.scandir(self.proj.TB_PATH) if f.is_dir()]
  
  def check_env(func):
    def wrapper(self, *args, **kwargs):
        if not self.has_project():
          Utils.error(f"initialize {self.proj.name} project first")
        func(self, *args, **kwargs)
    return wrapper

  def show_args(self) -> None:
    Utils.print(self.args)