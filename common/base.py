import sys
import time
import yaml
from const import *
from rich.console import Console

class Base:
  console  = Console()
  cfg_dict = None

  def __init__(self) -> None:
    pass

  @classmethod
  def print(cls, msg: str) -> None:
    Base.console.print(msg)

  @classmethod
  def info(cls, msg: str) -> None:
    Base.console.print(f"[green bold]INFO:[/green bold] {msg}")

  @classmethod
  def warning(cls, msg: str) -> None:
    Base.console.print(f"[yellow bold]WARNING:[/yellow bold] {msg}")

  @classmethod
  def error(cls, msg: str) -> None:
    Base.console.print(f"[red bold]ERROR:[/red bold] {msg}")
    sys.exit()

  @classmethod
  def run_with_animation(cls, msg: str, func, *args: tuple):
    with Base.console.status(f"[green bold]{msg}"):
      time.sleep(1)
      try:
        return func(*args)
      except Exception as e:
        Base.error(e)

  @classmethod
  def get_proj(self, name) -> dict:
    if (Base.cfg_dict == None):
      with open(PROJ_LIST, mode="r", encoding="utf-8") as f:
        Base.cfg_dict = yaml.load(f.read(), Loader=yaml.FullLoader)
    if (name in Base.cfg_dict.keys()):
      return Base.cfg_dict[name]
    else:
      Base.error(f"can't find {name}")