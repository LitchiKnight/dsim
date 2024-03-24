from command.init_cmd import InitCmd

class Router:
  def __init__(self) -> None:
    pass
  
  def do_init(self, args: tuple) -> None:
    init = InitCmd(args)
    init.run()