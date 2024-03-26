from common.utils import Utils

class Project:
  def __init__(self, name: str) -> None:
    self.name = name

  def show(self) -> None:
    Utils.print(vars(self))