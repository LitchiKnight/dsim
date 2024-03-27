import os
from config.env import Env
from common.utils import Utils

class BaseCmd:
  def __init__(self, args: tuple) -> None:
    self.args = args
    self.proj = Env.get_proj(args.project)

  def has_project(self) -> bool:
    return os.path.exists(self.proj.WORK_PATH)
  
  def has_module(self, module: str) -> bool:
    m_p = os.path.join(self.proj.TB_PATH, module)
    return os.path.exists(m_p)
  
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