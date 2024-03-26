from argparse import ArgumentParser
from common.router import Router

def create_parser() -> ArgumentParser:
  arg_parser = ArgumentParser(description='Automatic Digitial Verification Simulation Tool')
  sub_parser = arg_parser.add_subparsers()
  router     = Router()

  init = sub_parser.add_parser("init")
  init.add_argument("-p", "--project", type=str, required=True, help="target project name")
  init.add_argument("-f", "--force", action="store_true", help="force to initiate work space")
  init.add_argument("-t", "--tool", type=str, default="git", help="version control tool")
  init.add_argument("--no-pull", action="store_true", help="initiate project work space without pull remote repository")
  init.set_defaults(func = router.do_init)

  add = sub_parser.add_parser("add")
  add.add_argument("-p", "--project", type=str, required=True, help="target project name")
  add.add_argument("-m", "--module", type=str, required=True, help="target module name")
  add.set_defaults(func = router.do_add)

  remove = sub_parser.add_parser("remove")
  remove.add_argument("-p", "--project", type=str, required=True, help="target project name")
  remove.add_argument("-m", "--module", type=str, required=True, help="target module name")
  remove.set_defaults(func = router.do_remove)

  _list = sub_parser.add_parser("list")
  _list.add_argument("-p", "--project", type=str, required=True, help="target project name")
  _list.add_argument("-m", "--module", type=str, nargs="+", help="target module name")
  _list.set_defaults(func = router.do_list)

  return arg_parser

def main() -> None:
  parser = create_parser()
  args = parser.parse_args()
  args.func(args)

main()