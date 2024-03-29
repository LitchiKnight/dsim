import os
import shutil
from common.utils import Utils
from command.base import BaseCmd

class RemoveCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)

  def remove_project(self) -> None:
    project = self.proj.name
    w_p = self.proj.WORK_PATH
    Utils.run_with_animation(f"Removing {project} project...", shutil.rmtree, w_p, True)
    if os.path.exists(w_p):
      Utils.error(f"Unable to remove {project} project")
    Utils.info(f"Removed {project} project")

  def remove_module(self, module: str) -> None:
    project = self.proj.name
    m_p = os.path.join(self.proj.TB_PATH, module)
    if os.path.exists(m_p):
      Utils.run_with_animation(f"Removing {module} from {project}...", shutil.rmtree, m_p, True)
      if os.path.exists(m_p):
        Utils.error(f"Unable to remove {module} from {project}")
      Utils.info(f"Removed {module} from {project}")
    else:
      Utils.error(f"No such module: {module}")

  @BaseCmd.check_env
  def run(self) -> None:
    if self.args.module == None:
      self.remove_project()
    else:
      for module in self.args.module:
        self.remove_module(module)