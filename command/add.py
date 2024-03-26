import os
from config.env import Env
from common.utils import Utils
from command.base import BaseCmd

class AddCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)
    self.dir_template = Env.get_work_dir(args.module)

  @BaseCmd.check_env
  def run(self) -> None:
    project = self.proj.name
    module = self.args.module
    m_p = os.path.join(self.proj.TB_PATH, module)
    if not os.path.exists(m_p):
      Utils.run_with_animation(f"Adding {module} to {project}...", Utils.dict2dir, m_p, self.dir_template)
      Utils.info(f"create directory for {module} at {m_p}")
    else:
      Utils.warning(f"{module} already exists at {project}")
