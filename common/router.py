from command.init import InitCmd
from command.add import AddCmd
from command.remove import RemoveCmd
from command.list import ListCmd
from command.run import RunCmd

class Router:
  def __init__(self) -> None:
    pass

  def do_init(self, args: tuple) -> None:
    init = InitCmd(args)
    init.run()

  def do_add(self, args: tuple) -> None:
    add = AddCmd(args)
    add.run()

  def do_remove(self, args: tuple) -> None:
    remove = RemoveCmd(args)
    remove.run()

  def do_list(self, args: tuple) -> None:
    _list = ListCmd(args)
    _list.run()

  def do_run(self, args: tuple) -> None:
    run = RunCmd(args)
    run.run()