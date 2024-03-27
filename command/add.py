import os
from config.env import Env
from common.utils import Utils
from command.base import BaseCmd

class AddCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)

  def add_module(self, module: str) -> None:
    project = self.proj.name
    dir_template = Env.get_work_dir(module)
    m_p = os.path.join(self.proj.TB_PATH, module)
    if not os.path.exists(m_p):
      Utils.run_with_animation(f"Adding {module} to {project}...", Utils.dict2dir, m_p, dir_template)
      if not os.path.exists(m_p):
        Utils.error(f"Unable to create {module} module")
      Utils.info(f"Create directory for {module} at {m_p}")
    else:
      Utils.warning(f"{module} already exists at {project}")

  @BaseCmd.check_env
  def run(self) -> None:
    for module in self.args.module:
      self.add_module(module)