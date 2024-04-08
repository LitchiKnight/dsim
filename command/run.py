import os
import re
import copy
import shutil
import subprocess
from common.const import *
from common.utils import Utils
from command.base import BaseCmd
from data.testcase import TestCase
from common.tclparse import TestCaseListParser
from concurrent.futures import ThreadPoolExecutor

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
  
  def get_cmd(self) -> tuple:
    cmd = self.config.get_simulator_cmd(self.args.simulator)
    cmp_cmd_list = []
    sim_cmd = ""
    if self.args.simulator == "vcs":
      cmp_cmd_list = cmd["compile"]["cmd"]
      sim_cmd      = cmd["sim"]["cmd"].strip()
      for i, cmp_cmd in enumerate(cmp_cmd_list):
        if ("cov_opts" in cmp_cmd) and self.args.coverage:
          cmp_cmd_list[i] = cmp_cmd.replace("<cov_opts>", cmd["compile"]["cov_opts"])
        else:
          cmp_cmd_list[i] = cmp_cmd.replace("<cov_opts>", "")
      if ("cov_opts" in sim_cmd) and self.args.coverage:
        sim_cmd = sim_cmd.replace("<cov_opts>", cmd["sim"]["cov_opts"])
      else:
        sim_cmd = sim_cmd.replace("<cov_opts>", "")
    return cmp_cmd_list, sim_cmd
    
  def set_env_var(self) -> None:
    os.environ["RTL_PATH"] = self.env["RTL_PATH"]
    os.environ["TB_PATH"]  = self.env["TB_PATH"]
    os.environ["SIM_PATH"] = self.env["SIM_PATH"]
    os.environ["UVM_HOME"] = self.env["UVM_HOME"]

  def gen_cmp_item(self, cmd_list: str) -> str:
    cmp_item = {"cmd": [], "out": ""}
    module = self.args.module
    cmp_out = os.path.join(self.env["SIM_PATH"], module, "build")
    if self.args.simulator == "vcs":
      build_lst_p = os.path.join(self.env["TB_PATH"], BUILD_LST_DIR)
      cmp_opts = self.args.cmp_opts
      for i, cmd in enumerate(cmd_list):
        cmd = cmd.replace("<dut_f>", os.path.join(build_lst_p, f"{module}_v.f"))
        cmd = cmd.replace("<c_f>", os.path.join(build_lst_p, f"{module}_c.f"))
        cmd = cmd.replace("<tb_f>", os.path.join(build_lst_p, f"{module}_sv.f"))
        cmd = cmd.replace("<cmp_out>", cmp_out)
        cmd = cmd.replace("<cmp_opts>", cmp_opts)
        cmd_list[i] = cmd
    cmp_item["cmd"] = cmd_list
    cmp_item["out"] = cmp_out
    return cmp_item
  
  def gen_sim_item(self, cmd: str, tc: TestCase) -> str:
    sim_item = {"cmd": "", "out": ""}
    module = self.args.module
    sim_out = os.path.join(self.env["SIM_PATH"], module, tc.name)
    if self.args.simulator == "vcs":
      plusarg = (tc.plusarg + self.args.plusarg).strip()
      sim_opts = f"+UVM_TESTNAME={tc.uvm_test} +UVM_VERBOSITY={self.args.verbosity} +UVM_MAX_QUIT_COUNT={self.args.quit} {plusarg}"
      cmd = cmd.replace("<sim_opts>", sim_opts)
      cmd = cmd.replace("<seed>", tc.seed)
      cmd = cmd.replace("<testcase>", tc.name)
      cmd = cmd.replace("<cmp_out>", os.path.join(self.env["SIM_PATH"], module, "build"))
      cmd = cmd.replace("<sim_out>", sim_out)
    sim_item["cmd"] = cmd
    sim_item["out"] = sim_out
    return sim_item

  def check_args(self) -> None:
    if self.args.compile_only and self.args.simulate_only:
      Utils.error("Invalid argument combination: -co/--compile_only and -so/--simulate_only both enabled")

  def do_clean(self, dir: str) -> None:
    shutil.rmtree(dir, ignore_errors=True)
    if os.path.exists(dir):
        Utils.warning(f"Unable to clean {dir}")

  def create_dir(self, dir: str) -> None:
    os.makedirs(dir, exist_ok=True)
    if not os.path.exists(dir):
      Utils.error(f"Unable to create {dir}")

  def do_compile(self, cmp_item: dict) -> None:
    if self.args.clean:
      self.do_clean(cmp_item["out"])
    self.create_dir(cmp_item["out"])
    # temp TODO
    with open(os.path.join(cmp_item["out"], "comp.log"), mode="w", encoding="utf-8") as f:
      Utils.print(cmp_item["cmd"])
      f.writelines(cmp_item["cmd"])

  def do_simulate(self, sim_item: dict) -> None:
    if self.args.clean:
      self.do_clean(sim_item["out"])
    self.create_dir(sim_item["out"])
    # temp TODO
    with open(os.path.join(sim_item["out"], "sim.log"), mode="w", encoding="utf-8") as f:
      Utils.print(sim_item["cmd"])
      f.write(sim_item["cmd"])

  def do_regression(self, sim_item_pool: list) -> None:
    with ThreadPoolExecutor(max_workers=5) as pool:
      pool.map(self.do_simulate, sim_item_pool)

  @BaseCmd.check_env
  def run(self) -> None:
    tc_lst = self.get_tc_lst()
    cmp_cmd, sim_cmd = self.get_cmd()
    
    self.check_args()
    self.set_env_var()

    if not self.args.simulate_only:
      cmp_item = self.gen_cmp_item(cmp_cmd)
      self.do_compile(cmp_item)
    
    if not self.args.compile_only:
      tc_dup = None
      if self.args.testcase:
        if re.match(".*_[0-9]+$", self.args.testcase):
          for tc in tc_lst:
            if tc.name == re.sub("_[0-9]+$", "_@seed", self.args.testcase):
              tc_dup = copy.deepcopy(tc)
              tc_dup.name = self.args.testcase
              tc_dup.seed = re.search("[0-9]+$", self.args.testcase).group()
        if tc_dup != None:
          sim_item = self.gen_sim_item(sim_cmd, tc_dup)
          self.do_simulate(sim_item)
        else:
          Utils.error(f"Can't find {self.args.testcase} in target testcase list")
      else:
        tc_pool = []
        for tc in tc_lst:
          for i in range(tc.seed[0], tc.seed[1]+1):
            tc_dup = copy.deepcopy(tc)
            tc_dup.name = tc.name.replace("@seed", str(i))
            tc_dup.seed = str(i)
            tc_pool.append(tc_dup)
        sim_item_pool = map(lambda x: self.gen_sim_item(sim_cmd, x), tc_pool)
        self.do_regression(sim_item_pool)
