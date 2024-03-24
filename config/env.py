import os
import yaml
from common.const import *
from common.base import Base
from config.proj_item import ProjItem

class Env:
  _proj_dict = None

  def __init__(self) -> None:
    pass

  @classmethod
  def get_proj(self, name: str) -> ProjItem:
    if (Env._proj_dict == None):
      proj_list_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        PROJ_LIST
      )
      try:
        with open(proj_list_file, mode="r", encoding="utf-8") as f:
          Env._proj_dict = yaml.load(f.read(), Loader=yaml.FullLoader)
      except Exception as e:
        Base.error(e)
    if (name in Env._proj_dict.keys()):
      user     = "TODO"
      p_i      = ProjItem()
      p_i.name = name
      for (k, v) in Env._proj_dict[name].items():
        if ("<user>" in v):
          v = v.replace("<user>", user)
        p_i.__setattr__(k, v)
      return p_i
    else:
      Base.error(f"No such project {name}, please check!")