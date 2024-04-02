import os
import re
import copy
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
    module = self.args.module
    _list = self.args.list
    if not self.has_module(module):
      Utils.error(f"No such module: {module}")
    elif not self.has_list(module, _list):
      Utils.error(f"No such file: {_list}")
    elif os.path.splitext(_list)[1] != ".lst":
      Utils.error(f"Unrecognized file: {_list}")
    else:
      return self.tclparser.parse_list(self.get_list_path(module, _list), True)

  @BaseCmd.check_env
  def run(self) -> None:
    tc_lst = self.get_tc_lst()
    tc_pool = []
    if self.args.testcase:
      tc_tpl_n = re.sub("_[0-9]+$", "_@seed", self.args.testcase)
      for tc in tc_lst:
        if tc.name == tc_tpl_n:
          tc_dup = copy.deepcopy(tc)
          tc_dup.name = self.args.testcase
          tc_dup.seed = re.search("[0-9]+$", self.args.testcase).group()
          tc_pool.append(tc_dup)
      if len(tc_pool) == 0:
        Utils.error(f"Unrecognized testcase: {self.args.testcase}")
    else:
      for tc in tc_lst:
        for i in range(tc.seed[0], tc.seed[1]+1):
          tc_dup = copy.deepcopy(tc)
          tc_dup.name = re.sub("@seed", str(i), tc.name)
          tc_dup.seed = str(i)
          tc_pool.append(tc_dup)

    for tc in tc_pool:
      Utils.print(vars(tc))