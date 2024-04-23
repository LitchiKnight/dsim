from enum import Enum

# env
BUILD_LST_DIR = "build/file_lst"
TC_LST_DIR = "tc_lst"

# default arguments
VER_CTRL_SYS = "git"
SIMULATOR = "vcs"
MAX_QUIT_COUNT = "2"
VERBOSITY = "UVM_MEDIUM"
DEBUGER = "verdi"

# cmd status
class CmdStatus(Enum):
  NONE = 0
  PASS = 1
  FAIL = 2
  ERROR = 3
  INTERRUPT = 4
  TIMEOUT = 5

# regression report format
TC_WIDTH = 50
SEED_WIDTH = 20
RESULT_WIDTH = 12
TIME_WIDTH = 20
INFO_WIDTH = 140

# patterns
SIM_ERR_PAT = "^(UVM_ERROR|UVM_FATAL|Error)"
SIM_END_PAT = "UVM Report Summary"