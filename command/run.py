import os
import re
import copy
from common.const import *
from config.env import Env
from common.utils import Utils
from command.base import BaseCmd
from data.testcase import TestCase
from common.tclparse import TestCaseListParser
from sim.vcs import Vcs
from concurrent.futures import ThreadPoolExecutor

class RunCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)
    self.regress = True
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
    
  def set_env_var(self) -> None:
    os.environ["RTL_PATH"] = self.proj.RTL_PATH
    os.environ["TB_PATH"]  = self.proj.TB_PATH
    os.environ["SIM_PATH"] = self.proj.SIM_PATH
    os.environ["UVM_HOME"] = self.proj.UVM_HOME

  def complete_vcs_cmp_cmd(self, cmd: str) -> str:
    module = self.args.module
    build_lst_p = os.path.join(self.proj.TB_PATH, BUILD_LST_DIR)
    cmd = cmd.replace("<dut_f>", os.path.join(build_lst_p, f"{module}_v.f"))
    cmd = cmd.replace("<c_f>", os.path.join(build_lst_p, f"{module}_c.f"))
    cmd = cmd.replace("<tb_f>", os.path.join(build_lst_p, f"{module}_sv.f"))
    cmd = cmd.replace("<cmp_out>", os.path.join(self.proj.SIM_PATH, module, "build"))
    return cmd
  
  def complete_vcs_sim_cmd(self, cmd: str, tc: TestCase) -> str:
    module = self.args.module
    sim_opts = f"+UVM_TESTNAME={tc.uvm_test}"
    cmd = cmd.replace("<sim_opts>", sim_opts)
    cmd = cmd.replace("<seed>", tc.seed)
    cmd = cmd.replace("<testcase>", tc.name)
    cmd = cmd.replace("<cmp_out>", os.path.join(self.proj.SIM_PATH, module, "build"))
    cmd = cmd.replace("<sim_out>", os.path.join(self.proj.SIM_PATH, module, tc.name))
    return cmd

  @BaseCmd.check_env
  def run(self) -> None:
    tc_lst = self.get_tc_lst()
    tc_pool = []
    if self.args.testcase:
      self.regress = False
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
          tc_dup.name = tc.name.replace("@seed", str(i))
          tc_dup.seed = str(i)
          tc_pool.append(tc_dup)

    vcs = Vcs()
    temp_cmp_cmd, temp_sim_cmd = vcs.get_command(cov=True)
    self.set_env_var()

    cmp_cmd = self.complete_vcs_cmp_cmd(temp_cmp_cmd)
    cmp_out = os.path.join(self.proj.SIM_PATH, self.args.module, "build")
    vcs.do_compile(cmp_cmd, cmp_out)

    sim_cmd_pool = map(lambda x: self.complete_vcs_sim_cmd(temp_sim_cmd, x), tc_pool)
    if self.regress:
      with ThreadPoolExecutor(max_workers=5) as pool:
        pool.map(vcs.do_simulate, sim_cmd_pool)
    else:
      sim_cmd = self.complete_vcs_sim_cmd(temp_sim_cmd, tc_pool[0])
      vcs.do_simulate(sim_cmd)
