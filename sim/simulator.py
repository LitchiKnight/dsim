class Simulator:
  def __init__(self) -> None:
    self.comp_res = False
    self.sim_res = False

  def get_command(self) -> str:
    pass

  def do_compile(self, cmp_cmd: str, cmp_out: str) -> None:
    pass

  def do_simulate(self, sim_cmd: str, sim_out: str) -> None:
    pass