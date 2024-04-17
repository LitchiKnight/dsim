from common.utils import Utils

class TestCase:
  def __init__(self, name: str) -> None:
    self.name = name
    self.uvm_test = ""
    self.seed = []
    self.plusarg = ""
  
  def show(self) -> None:
    Utils.print(vars(self))
