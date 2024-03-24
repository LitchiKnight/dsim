import argparse
from command.router import Router

def create_parser() -> argparse.ArgumentParser:
  arg_parser = argparse.ArgumentParser(description='Automatic Digitial Verification Simulation Tool')
  sub_parser = arg_parser.add_subparsers()
  router     = Router()

  init = sub_parser.add_parser("init")
  init.add_argument("project", type=str, help="target project name")
  init.add_argument("-f", "--force", action="store_true", help="force to initiate work space")
  init.add_argument("-t", "--tool", type=str, default="git", help="version control tool")
  init.set_defaults(func = router.do_init)

  return arg_parser

def main() -> None:
  parser = create_parser()
  args   = parser.parse_args()
  args.func(args)

main()