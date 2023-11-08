from rich.console import Console

class Parser:
    def __init__(self) -> None:
        self.svn_addr   = None
        self.disk       = None
        self.project    = None
        self.department = None
        self.user       = None

    def parse_config_file(self, file):
        with open(file, "r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line == '\n':
                    continue
                line  = line.replace('\n', '')
                key   = line.split("=")[0]
                value = line.split("=")[1]
                exec(f"self.{key} = \"{value}\"")

    def get_user(self):
        pass

    def gen_ws_path(self):
        return f"/remote/{self.disk}/{self.project}a/{self.department}/{self.user}/svnwork/{self.project}a_l/trunk/{self.department}/dv/v1.0"

    def print(self):
        c = Console()
        c.print(vars(self))