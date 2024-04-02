import os
import re
import yaml
import time
import subprocess
from common.const import *
from common.utils import Utils
from sim.simulator import Simulator

class Vcs(Simulator):
  def __init__(self) -> None:
    super().__init__()

  def gen_cmp_cmd(self, compile: dict, cov: bool = False) -> str:
    cmp_cmd = compile["cmd"].strip()
    cov_opts = ""
    if ("cov_opts" in compile) and cov:
      cov_opts = compile["cov_opts"].strip()
    cmp_cmd = cmp_cmd.replace("<cov_opts>", cov_opts)
    return cmp_cmd
  
  def gen_sim_cmd(self, sim: dict, cov: bool = False) -> str:
    sim_cmd = sim["cmd"].strip()
    cov_opts = ""
    if ("cov_opts" in sim) and cov:
      cov_opts = sim["cov_opts"].strip()
    sim_cmd = sim_cmd.replace("<cov_opts>", cov_opts)
    return sim_cmd

  def get_command(self, cov: bool = False) -> tuple:
    vcs_yaml_f = os.path.join(
      os.path.dirname(os.path.abspath(__file__)), "tools", "vcs.yaml"
    )
    with open(vcs_yaml_f, mode="r", encoding="utf-8") as f:
      content = f.read()
      vcs_yaml = yaml.load(content, Loader=yaml.FullLoader)
    cmp_cmd = self.gen_cmp_cmd(vcs_yaml['compile'], cov)
    sim_cmd = self.gen_sim_cmd(vcs_yaml["sim"], cov)
    return cmp_cmd, sim_cmd
  
  def do_compile(self, cmp_cmd: str, cmp_out: str) -> None:
    Utils.print(cmp_cmd)


  def do_simulate(self, sim_cmd: str, sim_out: str) -> None:
    Utils.print(sim_cmd)