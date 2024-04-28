from common.utils import Utils
from common.const import *
from data.simresult import SimResult

class Statistic:
  def __init__(self) -> None:
    self.total = 0
    self.count = 0
    self.pass_num = 0
    self.fail_num = 0
    self.timeout_num = 0
    self.exception_num = 0
    self.sim_res_list = []

  def add_sim_res(self, sim_res: SimResult) -> None:
    self.sim_res_list.append(sim_res)

  def get_sim_res(self, tc_name: str) -> SimResult:
    for sim_res in self.sim_res_list:
      if sim_res.name == tc_name:
        return sim_res
    return None
  
  def set_tc_status(self, tc_name: str, status: CmdStatus) -> None:
    for sim_res in self.sim_res_list:
      if sim_res.name == tc_name:
        sim_res.status = status
        if status == CmdStatus.PASS:
          self.pass_num += 1
        elif status == CmdStatus.FAIL:
          self.fail_num += 1
        elif status == CmdStatus.TIMEOUT:
          self.timeout_num += 1
        else:
          self.exception_num += 1
        self.count += 1
        break

  def set_tc_time(self, tc_name: str, time: float) -> None:
    for sim_res in self.sim_res_list:
      if sim_res.name == tc_name:
        sim_res.time = time
        break

  def set_tc_info(self, tc_name: str, info: str) -> None:
    for sim_res in self.sim_res_list:
      if sim_res.name == tc_name:
        sim_res.info = info
        break

  def print_curr_state(self, tc_name: str) -> None:
    sim_res = self.get_sim_res(tc_name)
    Utils.print("--------------------------------------------------------------")
    Utils.print(f"TESTCASE: {tc_name}")
    Utils.print(f"RESULT  : {sim_res.status.name}")
    Utils.print(f"PROGRESS: {self.count}/{self.total}")
    Utils.print("--------------------------------------------------------------")

  def show(self) -> None:
    Utils.info(f"regression result: pass:{self.pass_num}, fail:{self.fail_num}, timeout: {self.timeout_num}, exception: {self.exception_num}")

  def gen_stat_detail(self) -> str:
    report = ""
    total_width = TC_WIDTH+SEED_WIDTH+RESULT_WIDTH+TIME_WIDTH+INFO_WIDTH+6
    divider = "-"*total_width+"\n"
    cols = "│{:<{}}│{:<{}}│{:<{}}│{:<{}}│{:<{}}│\n"
    report += divider
    report += cols.format(
      "Testcase", TC_WIDTH,
      "Seed", SEED_WIDTH,
      "Result", RESULT_WIDTH,
      "Time", TIME_WIDTH,
      "Info", INFO_WIDTH
    )
    report += divider
    for sim_res in self.sim_res_list:
      if len(sim_res.info) > INFO_WIDTH:
        info = sim_res.info[0:67]+"..."+sim_res.info[-70:]
      else:
        info = sim_res.info
      report += cols.format(
        sim_res.name, TC_WIDTH,
        sim_res.seed, SEED_WIDTH,
        sim_res.status.name, RESULT_WIDTH,
        sim_res.time, TIME_WIDTH,
        info, INFO_WIDTH
      )
    report += divider
    return report