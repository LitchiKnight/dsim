import os
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
  
  def killgroup(self, ps: subprocess.Popen):
    try:
        os.killpg(os.getpgid(ps.pid), signal.SIGKILL)
    except AttributeError: #killpg not available on windows
        ps.kill()

  def run_cmd(self, cmd: str, mask: bool = False, time_limit: float = 300) -> tuple:
    status = CmdStatus.NONE
    err_msg = ""
    start = time.time()
    try:
      ps = subprocess.Popen(cmd,
                            shell=True,
                            executable='/bin/bash',
                            universal_newlines=True,
                            start_new_session=True,
                            env=os.environ,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
      timer = threading.Timer(time_limit, self.killgroup, [ps])
      timer.start()
      self.ps_list.append(ps)
      while ps.poll() == None:
        output = ps.stdout.readline()
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
      if timer.is_alive():
        timer.cancel()
      else:
        status = CmdStatus.TIMEOUT
        err_msg = "program timeout"
    if status == CmdStatus.NONE:
      status = CmdStatus.PASS if ps.returncode == 0 else CmdStatus.FAIL
    consumption = time.time() - start
    return status, err_msg, consumption