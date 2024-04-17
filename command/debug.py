import os
from common.utils import Utils
from command.base import BaseCmd
from common.const import *

class DebugCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
      super().__init__(args)

  def get_cmd(self) -> str:
    module = self.args.module
    debuger = self.config.get_debug_cmd(self.args.debuger)
    cmd = debuger["cmd"]
    build_lst_p = os.path.join(self.env["TB_PATH"], BUILD_LST_DIR)
    cmd = cmd.replace("<dut_f>", os.path.join(build_lst_p, f"{module}_v.f"))
    cmd = cmd.replace("<c_f>", os.path.join(build_lst_p, f"{module}_c.f"))
    cmd = cmd.replace("<tb_f>", os.path.join(build_lst_p, f"{module}_sv.f"))
    cmd = cmd.replace("<top>", self.args.top)
    cmd = cmd.replace("<testcase>", self.args.testcase)
    return cmd
  
  def do_debug(self, cmd: str) -> None:
    sim_out = os.path.join(self.env["SIM_PATH"], self.args.module, self.args.testcase)
    os.chdir(sim_out)
    status, err_msg, _ = self.run_cmd(cmd)
    if status != CmdStatus.PASS:
      Utils.error(err_msg)

  def run(self) -> None:
    module = self.args.module
    if not self.has_module(module):
      Utils.error(f"No such module: {module}")
    cmd = self.get_cmd()
    self.do_debug(cmd)