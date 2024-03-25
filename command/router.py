from common.base import Base
from command.init_cmd import InitCmd
from command.add_cmd import AddCmd

class Router:
  def __init__(self) -> None:
    pass

  def do_init(self, args: tuple) -> None:
    init = InitCmd(args)
    init.run()

  def do_add(self, args: tuple) -> None:
    add = AddCmd(args)
    add.run()