import os
import re
from common.utils import Utils
from data.testcase import TestCase

class TestCaseListParser:
  def __init__(self) -> None:
    self._global = ""
    self.seed    = []

  def is_comment(self, line: str) -> bool:
    return not(re.match("^//", line) == None)
  
  def is_include(self, line: str) -> bool:
    return not(re.match("^`include", line) == None)

  def is_global(self, line: str) -> bool:
    return not(re.match("^global", line) == None)
  
  def is_seed(self, line: str) -> bool:
    return not(re.match("^@seed", line) == None)
  
  def is_testcase(self, line: str) -> bool:
    return not(re.match("^.*_@seed\s*\+UVM_TESTNAME=.*", line) == None)

  def parse_global(self, line: str) -> None:
    self._global += re.sub("global\s*=\s*", "", line)

  def parse_seed(self, line: str) -> None:
    seed = re.sub("@seed\s*=\s*", "", line).replace(":", ",")
    seed_l = eval(seed)
    if len(seed_l) != 2 or seed_l[0] > seed_l[1]:
      Utils.error(f"Invalid seed range: {seed_l}")
    else:
      self.seed = seed_l

  def parse_testcase(self, line: str) -> TestCase:
    cont = re.sub("//.*", "", line) # remove comment
    cont_l = cont.split(" ")
    tc = TestCase(cont_l[0])
    tc.uvm_test = cont_l[1].replace("+UVM_TESTNAME=", "")
    tc.seed = self.seed
    tc.plusarg += self._global
    for item in cont_l[2:]:
      tc.plusarg += f" {item}"
    return tc
  
  def reset_property(self) -> None:
    self._global = ""
    self.seed    = []

  def parse_list(self, file: any, inc_en: bool = False) -> list:
    tc_lst = []
    with open(file, mode="r", encoding="utf-8") as f:
      for line in f:
        line = line.strip()
        if not line or self.is_comment(line):
          continue
        elif self.is_include(line):
          if inc_en:
            inc_f = os.path.join(os.path.dirname(file), re.sub("`include\s*|\"", "", line))
            tc_lst += self.parse_list(inc_f, inc_en)
          else:
            continue
        elif self.is_global(line):
          self.parse_global(line)
        elif self.is_seed(line):
          self.parse_seed(line)
        elif self.is_testcase(line):
          tc = self.parse_testcase(line)
          tc_lst.append(tc)
    self.reset_property()
    return tc_lst