import os
from config.env import Env
from common.base import Base

class AddCmd:
  def __init__(self, args: tuple) -> None:
    self.args = args
    self.proj = Env.get_proj(args.project)
    self.dir_template = Env.get_work_dir(args.module)
    pass

  def dict2dir(self, base: any, template: dict) -> None:
    for k, v in template.items():
      path = os.path.join(base, k)
      if isinstance(v, dict):
        self.dict2dir(path, v)
      elif isinstance(v, list):
        os.makedirs(path, exist_ok=True)
        for f_n in v:
          f = open(os.path.join(path, f_n), "w")
          f.close()

  def create_module_dir(self) -> None:
    module = self.args.module
    m_p = os.path.join(self.proj.TB_PATH, module)
    if not os.path.exists(m_p):
      Base.run_with_animation(f"Creating {module} directory...", self.dict2dir, m_p, self.dir_template)
      Base.info(f"create directory for {module} at {m_p}")
    else:
      Base.warning(f"{module} already exist at {m_p}")

  def run(self) -> None:
    self.create_module_dir()