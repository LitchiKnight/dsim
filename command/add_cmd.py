import os
from config.env import Env
from common.base import Base

class AddCmd:
  def __init__(self, args: tuple) -> None:
    self.args = args
    self.proj = Env.get_proj(args.project)
    self.dir_template = Env.get_work_dir(args.module)

  def create_module_dir(self) -> None:
    project = self.args.project
    module = self.args.module
    m_p = os.path.join(self.proj.TB_PATH, module)
    if not os.path.exists(m_p):
      Base.run_with_animation(f"Adding {module} to {project}...", Base.dict2dir, m_p, self.dir_template)
      Base.info(f"create directory for {module} at {m_p}")
    else:
      Base.warning(f"{module} already exists at {project}")

  def run(self) -> None:
    self.create_module_dir()