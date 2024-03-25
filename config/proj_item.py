from common.base import Base

class ProjItem:
  def __init__(self, name: str) -> None:
    self.name = name

  def show(self) -> None:
    Base.print(vars(self))