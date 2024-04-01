from config.env import Env

class Simulator:
  def __init__(self, args: tuple) -> None:
    self.args = args
    self.proj = Env.get_proj(args.project)
    self.comp_res = False
    self.sim_res = False

  def get_command(self) -> str:
    pass

  def do_compile(self) -> None:
    pass

  def do_simulate(self) -> None:
    pass