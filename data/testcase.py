from common.base import Base

class TestCase:
  def __init__(self, name: str) -> None:
    self.name = name
    self.uvm_test = ""
    self.seed = []
    self.plusarg = ""

  def is_valid(self) -> bool:
    if self.uvm_test == "":
      return False
    if len(self.seed) != 2 or self.seed[0] > self.seed[1]:
      return False