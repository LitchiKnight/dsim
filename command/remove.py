import os
import shutil
from common.utils import Utils
from command.base import BaseCmd

class RemoveCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)

  @BaseCmd.check_env
  def run(self) -> None:
    project = self.proj.name
    module = self.args.module
    m_p = os.path.join(self.proj.TB_PATH, module)
    if os.path.exists(m_p):
      try:
        Utils.run_with_animation(f"Removing {module} from {project}...", shutil.rmtree, m_p)
      except Exception as e:
        Utils.error(e)
      Utils.info(f"removed {module} from {project}")
    else:
      Utils.error(f"No such module at {project}")