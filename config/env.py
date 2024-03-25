import os
import yaml
import getpass
from common.base import Base
from data.project import Project

class Env:
  def __init__(self) -> None:
    pass

  @classmethod
  def get_proj(self, name: str) -> Project:
    proj_list_file = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "proj", f"{name}.yaml"
    )

    try:
      with open(proj_list_file, mode="r", encoding="utf-8") as f:
        content = f.read().format(user = getpass.getuser())
        proj_cfg = yaml.load(content, Loader=yaml.FullLoader)
    except FileNotFoundError:
      Base.error(f"No such project")
    except Exception as e:
      Base.error(e)

    p = Project(name)
    for k, v in proj_cfg.items():
      p.__setattr__(k, v)
    return p

  @classmethod
  def get_work_dir(self, module: str) -> dict:
    dir_cfg = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "dir", "work.yaml"
    )

    try:
      with open(dir_cfg, mode="r", encoding="utf-8") as f:
        content = f.read().format(module = module)
        dir = yaml.load(content, Loader=yaml.FullLoader)
    except Exception as e:
      Base.error(e)
    return dir
    
