import os
import shutil
from common.utils import Utils
from command.base import BaseCmd

class RemoveCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)

  def remove_project(self) -> None:
    project = self.args.project
    work_path = self.env["WORK_PATH"]
    Utils.run_with_animation(f"Removing {project} project...", shutil.rmtree, work_path, True)
    if os.path.exists(work_path):
      Utils.error(f"Unable to remove {project} project")
    Utils.info(f"Removed {project} project")

  def remove_module(self, module: str) -> None:
    project = self.args.project
    if self.has_module(module):
      Utils.run_with_animation(f"Removing {module} from {project}...", shutil.rmtree, self.get_module_path(module), True)
      if self.has_module(module):
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