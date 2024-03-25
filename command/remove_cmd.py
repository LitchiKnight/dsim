import os
import shutil
from common.base import Base
from config.env import Env

class RemoveCmd:
  def __init__(self, args: tuple) -> None:
    self.args = args
    self.proj = Env.get_proj(args.project)

  def run(self) -> None:
    project = self.args.project
    module = self.args.module
    m_p = os.path.join(self.proj.TB_PATH, module)
    if os.path.exists(m_p):
      try:
        Base.run_with_animation(f"Removing {self.args.module} from {project}...", shutil.rmtree, m_p)
      except Exception as e:
        Base.error(e)
      Base.info(f"removed {self.args.module} from {project}")
    else:
      Base.error(f"No such module at {project}")