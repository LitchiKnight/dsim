import os
import yaml
import getpass
from common.base import Base
from config.proj_item import ProjItem

class Env:
  def __init__(self) -> None:
    pass

  @classmethod
  def get_proj(self, name: str) -> ProjItem:
    proj_list_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "proj_env_cfg", f"{name}.yaml"
    )

    try:
      with open(proj_list_file, mode="r", encoding="utf-8") as f:
        content = f.read().format(user = getpass.getuser())
        proj_cfg = yaml.load(content, Loader=yaml.FullLoader)
    except FileNotFoundError:
      Base.error(f"No such project")
    except Exception as e:
      Base.error(e)

    p_i = ProjItem(name)
    for k, v in proj_cfg.items():
      p_i.__setattr__(k, v)
    return p_i

  @classmethod
  def get_work_dir(self, module: str) -> dict:
    dir_cfg = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "dir_struct", "work.yaml"
    )

    try:
      with open(dir_cfg, mode="r", encoding="utf-8") as f:
        content = f.read().format(module = module)
        dir = yaml.load(content, Loader=yaml.FullLoader)
    except Exception as e:
      Base.error(e)
    return dir
    
