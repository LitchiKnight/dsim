import sys
import time
from common.const import *
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
  def error(cls, msg: str, exit: bool = True) -> None:
    Utils._con.print(f"[red bold]ERROR:[/red bold] {msg}")
    if exit:
      sys.exit()

  @classmethod
  def run_with_animation(cls, msg: str, func: any, *args: tuple) -> any:
    with Utils._con.status(f"[green bold]{msg}"):
      time.sleep(1)
      try:
        return func(*args)
      except Exception as e:
        Utils.error(e)
