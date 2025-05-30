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

  def get_modules(self) -> list:
    m_l = []
    if self.args.module == None:
      m_l = self.fetch_modules()
    else:
      for module in self.args.module:
        if self.has_module(module):
          m_l.append(module)
        else:
          Utils.error(f"No such module: {module}")
    return m_l
  
  def get_tc_lst(self, module: str) -> dict:
    tc_lst = []
    f_l    = []
    if self.args.list == None:
      f_l = glob.glob(self.get_list_path(module, "*.lst"))
    else:
      for f in self.args.list:
        if not self.has_list(module, f):
          Utils.error(f"No such file: {f}")
        elif os.path.splitext(f)[1] != ".lst":
          Utils.error(f"Unrecognized file: {f}")
        else:
          f_l.append(self.get_list_path(module, f))
    for f in f_l:
      f_n = os.path.basename(f)
      tc_lst.append({f_n: self.tclparser.parse_list(f)})
    return {module: tc_lst}

  def show_tc_lst(self, tc_lst: any, level: int = 0, is_last: bool = False, pre_indent: str = "") -> None:
    indent = pre_indent
    if level > 0:
      indent += "└── " if is_last else "├── "
    if isinstance(tc_lst, dict):
      for i, (k, v) in enumerate(tc_lst.items()):
        Utils.print(f"{indent}{k}")
        if level > 0:
          pre_indent += "    " if is_last else "│   "
        self.show_tc_lst(v, level+1, (len(tc_lst)-1) == i, pre_indent)
    elif isinstance(tc_lst, list):
      if len(tc_lst) > 0:
        for i, item in enumerate(tc_lst):
          self.show_tc_lst(item, level, (len(tc_lst)-1) == i, pre_indent)
    elif isinstance(tc_lst, TestCase):
      Utils.print(f"{indent}{tc_lst.name}")

  @BaseCmd.check_env
  def run(self) -> None:
    m_l = self.get_modules()
    if len(m_l) > 0:
      for m in m_l:
        tc_lst = Utils.run_with_animation(f"Searching {m} testcase...", self.get_tc_lst, m)
        Utils.info(f"{m} testcase list below")
        self.show_tc_lst(tc_lst)
    else:
      Utils.warning(f"empty work space")