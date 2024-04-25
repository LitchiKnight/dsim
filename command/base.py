import os
import re
import time
import errno
import signal
import threading
import subprocess
from common.config import Config
from common.utils import Utils
from common.const import *

class BaseCmd:
  def __init__(self, args: tuple) -> None:
    self.args = args
    self.config = Config()
    self.env = self.config.get_env(args.project)
    self.ps_list = []

  def get_module_path(self, module: str) -> str:
    return os.path.join(self.env["TB_PATH"], module)
  
  def get_list_path(self, module: str, _list: str) -> str:
    return os.path.join(self.env["TB_PATH"], module, TC_LST_DIR, _list)

  def has_project(self) -> bool:
    return os.path.exists(self.env["WORK_PATH"])
  
  def has_module(self, module: str) -> bool:
    return os.path.exists(self.get_module_path(module))
  
  def has_list(self, module: str, _list: str) -> bool:
    return os.path.exists(self.get_list_path(module, _list))
  
  def fetch_modules(self) -> list:
    if os.path.exists(self.env["TB_PATH"]):
      return [f.name for f in os.scandir(self.env["TB_PATH"]) if f.is_dir()]
    else:
      return []
  
  def check_env(func):
    def wrapper(self, *args, **kwargs):
        if not self.has_project():
          Utils.error(f"initialize {self.args.project} project first")
        func(self, *args, **kwargs)
    return wrapper

  def show_args(self) -> None:
    Utils.print(self.args)

  def create_dir(self, dir: str) -> None:
    os.makedirs(dir, exist_ok=True)
    if not os.path.exists(dir):
      Utils.error(f"Unable to create {dir}")

  def dict2dir(self, base: any, template: dict) -> None:
    for k, v in template.items():
      path = os.path.join(base, k)
      if isinstance(v, dict):
        self.dict2dir(path, v)
      elif isinstance(v, list):
        self.create_dir(path)
        for f_n in v:
          f = open(os.path.join(path, f_n), "w")
          f.close()

  def link_dir(self, src: str, dst: str) -> None:
    file_list = os.listdir(src)
    path_pair = map(lambda x: {"src": os.path.join(src, x), "dst": os.path.join(dst, x)}, file_list)
    for item in path_pair:
      try:
        os.symlink(item["src"], item["dst"])
      except OSError as e:
        if e.errno == errno.EEXIST:
          os.remove(item["dst"])
          os.symlink(item["src"], item["dst"])
        else:
          Utils.error(e)
      finally:
        if not os.path.islink(item["dst"]):
          link = item["src"]
          Utils.error(f"unable to link \'{link}\'")
  
  def catch_err_on_the_fly(self, line: str) -> tuple:
    catched = False
    end = False
    if re.match(SIM_ERR_PAT, line):
      catched = True
    if SIM_END_PAT in line:
      end = True
    return catched, end

  def killgroup(self, ps: subprocess.Popen):
    try:
        os.killpg(os.getpgid(ps.pid), signal.SIGKILL)
    except AttributeError: #killpg not available on windows
        ps.kill()

  def run_cmd(self, cmd: str, mask: bool = False, time_limit: float = 300) -> tuple:
    ps = None
    timer = None
    status = CmdStatus.NONE
    err_msg = ""
    start = time.time()
    catched = False
    chk_end = False
    stdout_fd = None
    try:
      ps = subprocess.Popen(cmd,
                            shell=True,
                            executable='/bin/bash',
                            universal_newlines=True,
                            start_new_session=True,
                            env=os.environ,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
      stdout_fd = ps.stdout.fileno()
      timer = threading.Timer(time_limit, self.killgroup, args=(ps))
      timer.start()
      self.ps_list.append(ps)
      while ps.poll() == None:
        output = ps.stdout.readline()
        if not (catched or chk_end):
          catched, chk_end = self.catch_err_on_the_fly(output)
          if catched:
            err_msg = output.strip()
        if not mask and output:
          print(output, end="")
    except subprocess.CalledProcessError:
      status = CmdStatus.ERROR
      err_msg = ps.communicate()[0]
      self.killgroup(ps)
    except KeyboardInterrupt:
      status = CmdStatus.INTERRUPT
      err_msg = "program interrputed"
      self.killgroup(ps)
    finally:
      os.close(stdout_fd)
      if timer and timer.is_alive():
        timer.cancel()
      else:
        status = CmdStatus.TIMEOUT
        err_msg = "program timeout"
    if status == CmdStatus.NONE:
      if ps.returncode == 0:
        status = CmdStatus.PASS if not catched else CmdStatus.FAIL
      else:
        status = CmdStatus.INTERRUPT
        err_msg = "program interrputed"
    consumption = time.time() - start
    return status, err_msg, consumption
