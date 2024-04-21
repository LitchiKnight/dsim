from common.const import *

class SimResult:
    def __init__(self, name: str) -> None:
        self.name = name
        self.seed = None
        self.status = SimStatus.NOT_START
        self.time = 0
        self.info = ""
