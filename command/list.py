import os
import glob
from common.utils import Utils
from common.const import *
from command.base import BaseCmd
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

  def show_tc_lst(self, tc_lst_d: dict) -> None:
    Utils.print(tc_lst_d) #TODO

  @BaseCmd.check_env
  def run(self) -> None:
    m_l = self.get_module_list()
    for m in m_l:
      self.show_tc_lst(self.get_tc_lst(m))