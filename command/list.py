import os
import glob
from common.utils import Utils
from common.const import *
from command.base import BaseCmd
from data.testcase import TestCase
from common.tclparse import TestCaseListParser

class ListCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)
    self.tclparser = TestCaseListParser()

  def get_module_list(self) -> list:
    m_l = []
    if self.args.module == None:
      m_l = self.fetch_modules()
    else:
      for module in self.args.module:
        if self.has_module(module):
          m_l.append(module)
        else:
          Utils.error(f"{module} module does not exists in {self.proj.name}")
    return m_l
  
  def get_tc_lst(self, module: str) -> dict:
    tc_lst_d = {module: []}
    tc_lst_pat = os.path.join(self.proj.TB_PATH, module, TC_LST_DIR, "*.lst")
    f_l = glob.glob(tc_lst_pat)
    for f in f_l:
      f_n = os.path.basename(f)
      tc_lst = self.tclparser.parse_list(f)
      tc_lst_d[module].append({f_n: tc_lst})
    return tc_lst_d

  def tc_content(self, tc: TestCase) -> str:
    return f"{tc.name} {tc.seed}"

  def show_tc_lst(self, tc_lst: any, level: int) -> None:
    indent = "\t"*level
    if isinstance(tc_lst, dict):
      for k, v in tc_lst.items():
        Utils.print(f"{indent}{k}:")
        self.show_tc_lst(v, level+1)
    elif isinstance(tc_lst, list):
      if len(tc_lst) == 0:
        Utils.print(f"{indent}empty list")
      else:
        for item in tc_lst:
          self.show_tc_lst(item, level)
    elif isinstance(tc_lst, TestCase):
      Utils.print(f"{indent}{self.tc_content(tc_lst)}")

  @BaseCmd.check_env
  def run(self) -> None:
    m_l = self.get_module_list()
    for m in m_l:
      Utils.info(f"{m} testcase list below")
      self.show_tc_lst(self.get_tc_lst(m), 0)