import os
import re
import sys
import copy
import shutil
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
        cmd_list[i] = cmd.strip()
    cmp_item["cmd"] = cmd_list
    cmp_item["out"] = cmp_out
    return cmp_item
  
  def replace_between(self, text, start, end, repl):
    pattern = re.compile(re.escape(start) + "(.*?)" + re.escape(end))
    return re.sub(pattern, start + repl + end, text)

  def merge_plusarg(self, tc: TestCase) -> str:
    plusarg = tc.plusarg.strip()
    if "+UVM_VERBOSITY=" not in plusarg:
      verbosity = self.args.verbosity if self.args.verbosity else VERBOSITY
      plusarg += f" +UVM_VERBOSITY={verbosity}"
    elif self.args.verbosity:
      plusarg = self.replace_between(plusarg, "+UVM_VERBOSITY=", " ", self.args.verbosity)
    if "+UVM_MAX_QUIT_COUNT" not in plusarg:
      quit = self.args.quit if self.args.quit else MAX_QUIT_COUNT
      plusarg += f" +UVM_MAX_QUIT_COUNT={quit}"
    elif self.args.quit:
      plusarg = self.replace_between(plusarg, "+UVM_MAX_QUIT_COUNT=", " ", self.args.quit)
    if self.args.plusarg:
      arg_list = self.args.plusarg.split()
      for arg in arg_list:
        if re.match("\+(.*?)\=", arg):
          pattern = re.match("\+(.*?)\=", arg).group()
          value = re.search("=(.*)", arg).group(1)
          if pattern in plusarg:
            plusarg = self.replace_between(plusarg, pattern, " ", value)
          else:
            plusarg += f" {arg}"
        elif arg not in plusarg:
          plusarg += f" {arg}"
    return plusarg
  
  def gen_sim_item(self, cmd: str, tc: TestCase) -> str:
    sim_item = {"cmd": "", "out": ""}
    sim_out = os.path.join(self.env["SIM_PATH"], self.args.module, tc.name)
    if self.args.simulator == "vcs":
      sim_opts = f"+UVM_TESTNAME={tc.uvm_test} {self.merge_plusarg(tc)}"
      cmd = cmd.replace("<sim_opts>", sim_opts)
      cmd = cmd.replace("<seed>", tc.seed)
      cmd = cmd.replace("<testcase>", tc.name)
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

  def print_icon(self, status: int) -> None:
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    icon_dir = os.path.join(os.path.dirname(curr_dir), "icon")
    if status == CMD_PASS:
      with open(os.path.join(icon_dir, "pass.txt"), mode="r", encoding="utf-8") as f:
        for line in f.readlines():
          Utils.print(f"[green bold]{line.strip()}[/green bold]")
    else:
      with open(os.path.join(icon_dir, "fail.txt"), mode="r", encoding="utf-8") as f:
        for line in f.readlines():
          Utils.print(f"[red bold]{line.strip()}[/red bold]")

  def do_compile(self, cmp_item: dict, ignore_pass: bool = False) -> None:
    out = cmp_item["out"]
    if self.args.clean:
      self.do_clean(out)
    self.create_dir(out)
    os.chdir(out)
    for cmd in cmp_item["cmd"]:
      status = self.run_cmd(cmd)
      if status != CMD_PASS:
        break
    if not (status == CMD_PASS and ignore_pass):
      self.print_icon(status)
      Utils.info(f"output directory: {out}")
    if status != CMD_PASS:
      sys.exit()

  def do_simulate(self, sim_cmd: str, tc: TestCase, print_en: bool = True) -> None:
    sim_item = self.gen_sim_item(sim_cmd, tc)
    cmp_out = os.path.join(self.env["SIM_PATH"], self.args.module, "build")
    sim_out = sim_item["out"]
    if self.args.clean:
      self.do_clean(sim_out)
    self.create_dir(sim_out)
    self.link_dir(cmp_out, sim_out)
    os.chdir(sim_out)
    status = self.run_cmd(sim_item["cmd"], print_en)
    if status == CMD_PASS:
      try:
        with open(os.path. join(sim_out, f"{tc.name}.log"), mode="r", encoding="utf-8") as f:
          content = f.read()
          error_count = len(re.findall("Error", content))
          uvm_error_count = int(re.search("UVM_ERROR\s *: \s*([0-9]*)", content).group(1))
          uvm_fatal_count = int(re.search("UVM_FATAL\s *: \s*([0-9]*)", content).group(1))
          if error_count > 0 or uvm_error_count > 0 or uvm_fatal_count > 0:
            status = CMD_FAIL
      except FileNotFoundError:
        Utils.error(f"can't find simulation log file at {sim_out}")
    if print_en:
      self.print_icon(status)
      Utils.info(f"output directory: {sim_out}")

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
      self.do_compile(cmp_item, not self.args.compile_only)
    
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
          self.do_simulate(sim_cmd, tc_dup)
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
