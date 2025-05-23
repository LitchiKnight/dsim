import os
import re
import sys
import copy
import shutil
import random
import threading
import concurrent.futures
from common.const import *
from common.utils import Utils
from command.base import BaseCmd
from data.testcase import TestCase
from data.simresult import SimResult
from data.statistic import Statistic
from common.tclparse import TestCaseListParser

class RunCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)
    self.tclparser = TestCaseListParser()
    self.stat = Statistic()
    self.sem = threading.Semaphore(1)
    self.cmp_dir = os.path.join(self.env["SIM_PATH"], self.args.module, "compile")
    self.res_dir = os.path.join(self.env["SIM_PATH"], self.args.module, "result")
    self.stat_dir = os.path.join(self.env["SIM_PATH"], self.args.module, "statistic")
    self.latest_dir = os.path.join(self.env["SIM_PATH"], self.args.module, "latest")

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
    for key in self.env.keys():
      if self.env[key]:
        os.environ[key] = self.env[key]

  def complete_cmp_cmd(self, cmd_list: list) -> list:
    # cmp_item = {"cmd": [], "out": ""}
    module = self.args.module
    # cmp_out = os.path.join(self.out_dir, "build")
    if self.args.simulator == "vcs":
      build_lst_p = os.path.join(self.env["TB_PATH"], module, BUILD_LST_DIR)
      cmp_opts = self.args.cmp_opts
      for i, cmd in enumerate(cmd_list):
        cmd = cmd.replace("<dut_f>", os.path.join(build_lst_p, f"{module}_v.f"))
        cmd = cmd.replace("<c_f>", os.path.join(build_lst_p, f"{module}_c.f"))
        cmd = cmd.replace("<tb_f>", os.path.join(build_lst_p, f"{module}_sv.f"))
        cmd = cmd.replace("<cmp_out>", self.cmp_dir)
        cmd = cmd.replace("<cmp_opts>", cmp_opts)
        cmd_list[i] = cmd.strip()
    return cmd_list
  
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
    sim_out = os.path.join(self.res_dir, tc.name)
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
    if self.args.testcase and self.args.rand_seed:
      Utils.error("random seed only can be used at regression senario")
    if self.args.timeout <= 0:
      Utils.error("timeout value must be greater than zero")
    if self.args.thread <= 0:
      Utils.error("thread value must be greater than zero")

  def do_clean(self, dir: str) -> None:
    shutil.rmtree(dir, ignore_errors=True)
    if os.path.exists(dir):
        Utils.warning(f"Unable to clean {dir}")

  def print_icon(self, status: CmdStatus) -> None:
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    icon_dir = os.path.join(os.path.dirname(curr_dir), "icon")
    if status == CmdStatus.PASS:
      with open(os.path.join(icon_dir, "pass.txt"), mode="r", encoding="utf-8") as f:
        for line in f.readlines():
          Utils.print(f"[green bold]{line.strip()}[/green bold]")
    else:
      with open(os.path.join(icon_dir, "fail.txt"), mode="r", encoding="utf-8") as f:
        for line in f.readlines():
          Utils.print(f"[red bold]{line.strip()}[/red bold]")

  def do_compile(self, cmd_lst: list, compile_only: bool = False) -> None:
    if self.args.clean:
      self.do_clean(self.cmp_dir)
    self.create_dir(self.cmp_dir)
    os.chdir(self.cmp_dir)
    for cmd in cmd_lst:
      status, err_msg, _ = self.run_cmd(cmd)
      if status != CmdStatus.PASS:
        break
    if status != CmdStatus.PASS and err_msg:
      Utils.error(err_msg, exit=False)
    if not (status == CmdStatus.PASS and not compile_only):
      self.print_icon(status)
      Utils.info(f"output directory: {self.cmp_dir}")
    if status != CmdStatus.PASS:
      sys.exit()

  def simulate_single_testcase(self, sim_cmd: str, tc: TestCase, is_regress: bool = False) -> tuple:
    with self.sem:
      sim_item = self.gen_sim_item(sim_cmd, tc)
      sim_out = sim_item["out"]
      if self.args.clean:
        self.do_clean(sim_out)
      self.create_dir(sim_out)
      self.link_dir(self.cmp_dir, sim_out)
      os.chdir(sim_out)
    status, err_msg, consumption = self.run_cmd(sim_item["cmd"], is_regress, self.args.timeout)
    with self.sem:
      self.stat.set_tc_status(tc.name, status)
      self.stat.set_tc_time(tc.name, str(consumption))
      self.stat.set_tc_info(tc.name, err_msg)
      if self.stat.total > 1:
        self.stat.print_curr_state(tc.name)
      else:
        self.print_icon(status)
        Utils.info(f"output directory: {sim_out}")

  def handle_statistic(self) -> None:
    detail = self.stat.gen_stat_detail()
    self.do_clean(self.stat_dir)
    os.makedirs(self.stat_dir, exist_ok=True)
    with open(os.path.join(self.stat_dir, "detail.log"), mode="w", encoding="utf-8") as f:
      f.write(detail)

  def do_simulate(self, sim_cmd: str, tc_lst: list) -> None:
    self.stat.total = len(tc_lst)
    for tc in tc_lst:
      sim_res = SimResult(tc.name)
      sim_res.seed = tc.seed
      self.stat.add_sim_res(sim_res)
    random.shuffle(tc_lst)
    if self.args.clean and self.stat.total > 1:
      self.do_clean(self.res_dir)
    with concurrent.futures.ThreadPoolExecutor(max_workers=self.args.thread) as pool:
      try:
        th_list = [pool.submit(self.simulate_single_testcase, sim_cmd, tc, (self.stat.total > 1)) for tc in tc_lst]
        concurrent.futures.wait(th_list)
      except KeyboardInterrupt:
        Utils.error("interrupt simulation", exit=False)
      except Exception as e:
        Utils.error(e, exit=False)
      finally:
        for th in th_list:
          th.cancel()
        for ps in self.ps_list:
          if ps.poll() == None:
            self.killgroup(ps)
        pool.shutdown()
    self.handle_statistic()
    if (self.stat.total > 1):
      self.stat.show()
      Utils.info(f"output directory: {self.stat_dir}")

  @BaseCmd.check_env
  def run(self) -> None:
    tc_lst = self.get_tc_lst()
    cmp_cmd, sim_cmd = self.get_cmd()
    tc_pool = []
    
    self.check_args()
    self.set_env_var()

    if not self.args.simulate_only:
      cmp_cmd_lst = self.complete_cmp_cmd(cmp_cmd)
      self.do_compile(cmp_cmd_lst, self.args.compile_only)
    
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
          tc_pool.append(tc_dup)
        else:
          Utils.error(f"Can't find {self.args.testcase} in target testcase list")
      else:
        for tc in tc_lst:
          for i in range(tc.seed[0], tc.seed[1]+1):
            if self.args.rand_seed:
              seed = abs(hash(random.random()))
            else:
              seed = i
            tc_dup = copy.deepcopy(tc)
            tc_dup.name = tc.name.replace("@seed", str(seed))
            tc_dup.seed = str(seed)
            tc_pool.append(tc_dup)
      self.do_simulate(sim_cmd, tc_pool)
