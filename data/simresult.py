from common.const import *

class SimResult:
    def __init__(self, name: str) -> None:
        self.name = name
        self.seed = None
        self.status = CmdStatus.CMD_NONE
        self.time = 0
        self.info = ""