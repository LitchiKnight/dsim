import argparse
from rich.console import Console
from init.create_ws import create_work_space

arg_parser = argparse.ArgumentParser(description='Datang Digital Verification Simulation tool')
console    = Console()

def main():
  arg_parser.add_argument('-cws', type=str, help="create work space")

  args = arg_parser.parse_args()

  if args.cws:
    module = args.cws
    create_work_space(module)

main()