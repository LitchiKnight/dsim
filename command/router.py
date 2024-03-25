from command.init_cmd import InitCmd
from command.add_cmd import AddCmd
from command.remove_cmd import RemoveCmd
from command.list_cmd import ListCmd

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