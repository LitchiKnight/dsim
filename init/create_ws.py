import os
import sys
from rich.console import Console
from init.ws_parser import Parser

c = Console()
p = Parser()

def create_work_space(module):
    c.print(f"Start create work space for {module}!", style="bold red")
    p.parse_config_file("init\config.txt")
    p.print()
    c.print(p.gen_ws_path())
