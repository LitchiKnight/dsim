import os
import shutil
import subprocess
from git import Repo
from common.utils import Utils
from command.base import BaseCmd

class InitCmd(BaseCmd):
  def __init__(self, args: tuple) -> None:
    super().__init__(args)

  def init_work_path(self) -> bool:
    w_p = self.proj.WORK_PATH
    if self.args.force:
      shutil.rmtree(w_p, ignore_errors=True)
      if os.path.exists(w_p):
        Utils.error(f"Unable removed {self.proj.name} project directory")
      Utils.info("delete work space existing files or directories")
    if not os.path.exists(w_p):
      os.makedirs(w_p)
      Utils.info(f"create new work space at {w_p}")
      return True
    else:
      Utils.warning(f"{self.proj.name} already exists at {w_p}")
      return False

  def pull_from_git(self) -> None:
    w_p = self.proj.WORK_PATH
    try:
      subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
      Utils.error("GIT is not installed")
    repo = Repo.init()
    remote = Utils.run_with_animation("Cloning remote repository", repo.clone_from, self.proj.git_repo, w_p)

  def pull_from_svn(self) -> None:
    try:
      subprocess.run(["svn", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
      Utils.error("SVN is not installed")
    
  def pull_remote_repo(self) -> None:
    if self.args.tool == "git":
      self.pull_from_git()
    elif self.args.tool == "svn":
      self.pull_from_svn()
    Utils.info(f"pull remote repository from {self.proj.git_repo}")

  def run(self) -> None:
    if self.init_work_path():
      if not self.args.no_pull:
        self.pull_remote_repo()

  def show(self) -> None:
    Utils.print(self.args)