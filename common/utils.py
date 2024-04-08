import os
import sys
import time
import errno
from rich.console import Console

class Utils:
  _con = Console()

  def __init__(self) -> None:
    pass

  @classmethod
  def print(cls, msg: str) -> None:
    Utils._con.print(msg)

  @classmethod
  def info(cls, msg: str) -> None:
    Utils._con.print(f"[green bold]INFO:[/green bold] {msg}")

  @classmethod
  def warning(cls, msg: str) -> None:
    Utils._con.print(f"[yellow bold]WARNING:[/yellow bold] {msg}")

  @classmethod
  def error(cls, msg: str) -> None:
    Utils._con.print(f"[red bold]ERROR:[/red bold] {msg}")
    sys.exit()

  @classmethod
  def run_with_animation(cls, msg: str, func: any, *args: tuple) -> any:
    with Utils._con.status(f"[green bold]{msg}"):
      time.sleep(1)
      try:
        return func(*args)
      except Exception as e:
        Utils.error(e)

  @classmethod
  def dict2dir(self, base: any, template: dict) -> None:
    for k, v in template.items():
      path = os.path.join(base, k)
      if isinstance(v, dict):
        self.dict2dir(path, v)
      elif isinstance(v, list):
        os.makedirs(path, exist_ok=True)
        for f_n in v:
          f = open(os.path.join(path, f_n), "w")
          f.close()

  @classmethod
  def link_dir(self, src: str, dst: str) -> None:
    file_list = os.listdir(src)
    path_pair = map(lambda x: {"src": os.path.join(src, x), "dst": os.path.join(dst, x)}, file_list)
    for item in path_pair:
      try:
        os.symlink(item["src"], item["dst"])
      except OSError as e:
        if e.errno == errno.EEXIST:
          os.remove(item["dst"])
          os.symlink(item["src"], item["dst"])
        else:
          Utils.error(e)
      finally:
        if not os.path.islink(item["dst"]):
          link = item["src"]
          Utils.error(f"unable to link \'{link}\'")