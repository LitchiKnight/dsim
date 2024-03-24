from common.base import Base

class ProjItem:
  def __init__(self) -> None:
    pass

  def show(self) -> None:
    Base.print(vars(self))