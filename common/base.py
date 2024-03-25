import os
import sys
import time
from rich.console import Console

class Base:
  _con = Console()

  def __init__(self) -> None:
    pass

  @classmethod
  def print(cls, msg: str) -> None:
    Base._con.print(msg)

  @classmethod
  def info(cls, msg: str) -> None:
    Base._con.print(f"[green bold]INFO:[/green bold] {msg}")

  @classmethod
  def warning(cls, msg: str) -> None:
    Base._con.print(f"[yellow bold]WARNING:[/yellow bold] {msg}")

  @classmethod
  def error(cls, msg: str) -> None:
    Base._con.print(f"[red bold]ERROR:[/red bold] {msg}")
    sys.exit()

  @classmethod
  def run_with_animation(cls, msg: str, func: any, *args: tuple) -> any:
    with Base._con.status(f"[green bold]{msg}"):
      time.sleep(1)
      try:
        return func(*args)
      except Exception as e:
        Base.error(e)

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