import os
from common.const import *
from config.env import Env
from common.utils import Utils
from command.base import BaseCmd
from data.testcase import TestCase
from common.tclparse import TestCaseListParser

class RunCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)
    self.tclparser = TestCaseListParser()

  def get_tc_lst(self) -> dict:
    tc_lst_p = os.path.join(self.proj.TB_PATH, self.args.module, TC_LST_DIR, self.args.list)
    return self.tclparser.parse_list(tc_lst_p, True)

  def run(self) -> None:
    tc_lst = self.get_tc_lst()
    if self.args.testcase:
      print(self.args.testcase)
    else:
      pass

    Utils.print(self.args)
    # Utils.print(self.get_tc_lst())
    for tc in tc_lst:
      Utils.print(vars(tc))