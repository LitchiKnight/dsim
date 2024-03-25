import os
from config.env import Env
from common.base import Base

class ListCmd:
  def __init__(self, args: tuple) -> None:
    self.args = args

  def run(self) -> None:
    Base.print(self.args)