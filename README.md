# Digital Verification Simulation Tool
A Python script use to make digital verification work more efficient. 

# Install
1. Install Python(Requires: Python >=3.6)
2. Install required packages:
  - rich==12.6.0
  - GitPython==3.1.20
  - pyyaml==6.0.1

# Feature
1. Create work space based on YAML configuration file and pull remote repository as need
2. Add module testbench directory and necessary files
3. Remove module directory locally
4. List existing testcase for each module
5. Compile and simulate specified testcase
6. Run regression test and show regression result
7. Open wareform file by debug tool

# Usage
Note: set your project key infomation(remote repository path/absolute path) at env.yaml first
```
usage: main.py [-h] {init,add,remove,list,run,debug} ...

Automatic Digitial Verification Simulation Tool

positional arguments:
  {init,add,remove,list,run,debug}

options:
  -h, --help            show this help message and exit
```
## init
```
usage: main.py init [-h] -p PROJECT [-f] [--ver-ctrl-sys VER_CTRL_SYS] [--no-pull]

options:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        target project name
  -f, --force           force to initiate work space
  --ver-ctrl-sys VER_CTRL_SYS
                        version control system
  --no-pull             initiate project work space without pull remote repository
```
## add
```
usage: main.py add [-h] -p PROJECT -m MODULE [MODULE ...]

options:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        target project name
  -m MODULE [MODULE ...], --module MODULE [MODULE ...]
                        target module name
```
## remove
```
usage: main.py remove [-h] -p PROJECT [-m MODULE [MODULE ...]]

options:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        target project name
  -m MODULE [MODULE ...], --module MODULE [MODULE ...]
                        target module name
```
## list
```
usage: main.py list [-h] -p PROJECT [-m MODULE [MODULE ...]] [-l LIST [LIST ...]]

options:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        target project name
  -m MODULE [MODULE ...], --module MODULE [MODULE ...]
                        target module name
  -l LIST [LIST ...], --list LIST [LIST ...]
                        target testcase list name
```
## run
```
usage: main.py run [-h] -p PROJECT -m MODULE -l LIST [-tc TESTCASE] [-cov] [-co] [-so] [-si SIMULATOR] [-q QUIT] [-rs] [-th THREAD] [--clean]
                   [--cmp-opts CMP_OPTS] [--plusarg PLUSARG] [--verbosity {UVM_NONE,UVM_LOW,UVM_MEDIUM,UVM_HIGH,UVM_FULL,UVM_DEBUG}] [--timeout TIMEOUT]

options:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        target project name
  -m MODULE, --module MODULE
                        target module name
  -l LIST, --list LIST  target testcase list name
  -tc TESTCASE, --testcase TESTCASE
                        target testcase name
  -cov, --coverage      enable coverage collection
  -co, --compile_only   compile without simulate
  -so, --simulate_only  simulate without compile
  -si SIMULATOR, --simulator SIMULATOR
                        target simulator
  -q QUIT, --quit QUIT  UVM simulation max quit count
  -rs, --rand_seed      execute regression with random seed
  -th THREAD, --thread THREAD
                        the number of threads executing in parallel
  --clean               clean simulation directories
  --cmp-opts CMP_OPTS   compile options
  --plusarg PLUSARG     simulation plusarg arguments
  --verbosity {UVM_NONE,UVM_LOW,UVM_MEDIUM,UVM_HIGH,UVM_FULL,UVM_DEBUG}
                        UVM verbosity level
  --timeout TIMEOUT     simulation time limit
```
## debug
```
usage: main.py debug [-h] -p PROJECT -m MODULE -tc TESTCASE [--top TOP] [-db DEBUGER]

options:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        target project name
  -m MODULE, --module MODULE
                        target module name
  -tc TESTCASE, --testcase TESTCASE
                        target testcase name
  --top TOP             target module top name
  -db DEBUGER, --debuger DEBUGER
                        target debuger
```