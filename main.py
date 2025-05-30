from argparse import ArgumentParser
from common.const import *
from common.router import Router

def create_parser() -> ArgumentParser:
  arg_parser = ArgumentParser(description='Automatic Digitial Verification Simulation Tool')
  sub_parser = arg_parser.add_subparsers()
  router     = Router()

  init = sub_parser.add_parser("init")
  init.add_argument("-p", "--project", type=str, required=True, help="target project name")
  init.add_argument("-f", "--force", action="store_true", help="force to initiate work space")
  init.add_argument("--ver-ctrl-sys", type=str, default=VER_CTRL_SYS, help="version control system")
  init.add_argument("--no-pull", action="store_true", help="initiate project work space without pull remote repository")
  init.set_defaults(func = router.do_init)

  add = sub_parser.add_parser("add")
  add.add_argument("-p", "--project", type=str, required=True, help="target project name")
  add.add_argument("-m", "--module", type=str, required=True, nargs="+", help="target module name")
  add.set_defaults(func = router.do_add)

  remove = sub_parser.add_parser("remove")
  remove.add_argument("-p", "--project", type=str, required=True, help="target project name")
  remove.add_argument("-m", "--module", type=str, nargs="+", help="target module name")
  remove.set_defaults(func = router.do_remove)

  _list = sub_parser.add_parser("list")
  _list.add_argument("-p", "--project", type=str, required=True, help="target project name")
  _list.add_argument("-m", "--module", type=str, nargs="+", help="target module name")
  _list.add_argument("-l", "--list", type=str, nargs="+", help="target testcase list name")
  _list.set_defaults(func = router.do_list)

  run = sub_parser.add_parser("run")
  run.add_argument("-p" , "--project", type=str, required=True, help="target project name")
  run.add_argument("-m" , "--module", type=str, required=True, help="target module name")
  run.add_argument("-l" , "--list", type=str, required=True, help="target testcase list name")
  run.add_argument("-tc", "--testcase", type=str, help="target testcase name")
  run.add_argument("-cov", "--coverage", action="store_true", help="enable coverage collection")
  run.add_argument("-co", "--compile_only", action="store_true", help="compile without simulate")
  run.add_argument("-so", "--simulate_only", action="store_true", help="simulate without compile")
  run.add_argument("-si", "--simulator", type=str, default=SIMULATOR, help="target simulator")
  run.add_argument("-q", "--quit", type=str, default="", help="UVM simulation max quit count")
  run.add_argument("-rs", "--rand_seed", action="store_true", help="execute regression with random seed")
  run.add_argument("-th", "--thread", type=int, default=5, help="the number of threads executing in parallel")
  run.add_argument("--clean", action="store_true", help="clean simulation directories")
  run.add_argument("--cmp-opts", type=str, default="", help="compile options")
  run.add_argument("--plusarg", type=str, default="", help="simulation plusarg arguments")
  run.add_argument("--verbosity", type=str, choices=["UVM_NONE", "UVM_LOW", "UVM_MEDIUM", "UVM_HIGH", "UVM_FULL", "UVM_DEBUG"], default="", help="UVM verbosity level")
  run.add_argument("--timeout", type=int, default=1800, help="simulation time limit")
  run.set_defaults(func = router.do_run)

  debug = sub_parser.add_parser("debug")
  debug.add_argument("-p" , "--project", type=str, required=True, help="target project name")
  debug.add_argument("-m" , "--module", type=str, required=True, help="target module name")
  debug.add_argument("-tc", "--testcase", type=str, required=True, help="target testcase name")
  debug.add_argument("--top", type=str, default="top", help="target module top name")
  debug.add_argument("-db", "--debuger", type=str, default=DEBUGER, help="target debuger")
  debug.set_defaults(func = router.do_debug)

  return arg_parser

def main() -> None:
  parser = create_parser()
  args = parser.parse_args()
  args.func(args)

if __name__ == "__main__":
  main()
