from common.utils import Utils
from data.testcase import TestCase

class TestCaseListParser:
  def __init__(self) -> None:
    pass

  def parse_list(self, file: any) -> list:
    tc_lst = []
    with open(file, mode="r", encoding="utf-8") as f:
      for line in f:
        Utils.print(line)
    return tc_lst