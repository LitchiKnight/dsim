import os
import shutil
import subprocess
from git import Repo
from config.env import Env
from common.base import Base

class InitCmd:
  def __init__(self, args: tuple) -> None:
    self.args = args
    self.proj = Env.get_proj(args.project)

  def init_work_path(self) -> bool:
    w_p = self.proj.WORK_PATH
    if self.args.force:
      try:
        shutil.rmtree(w_p)
      except Exception as e:
        Base.error(e)
      Base.info("delete work space existing files or directories")
    if not os.path.exists(w_p):
      os.makedirs(w_p)
      Base.info(f"create new work space at {w_p}")
      return True
    else:
      Base.warning(f"work space {w_p} already exists")
      return False

  def pull_from_git(self) -> None:
    w_p = self.proj.WORK_PATH
    try:
      subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
      Base.error("GIT is not installed")
    repo = Repo.init()
    remote = Base.run_with_animation("Cloning remote repository", repo.clone_from, self.proj.git_repo, w_p)

  def pull_from_svn(self) -> None:
    try:
      subprocess.run(["svn", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
      Base.error("SVN is not installed")
    
  def pull_remote_repo(self) -> None:
    if self.args.tool == "git":
      self.pull_from_git()
    elif self.args.tool == "svn":
      self.pull_from_svn()
    Base.info(f"pull remote repository from {self.proj.git_repo}")

  def run(self) -> None:
    if self.init_work_path():
      if not self.args.no_pull:
        self.pull_remote_repo()

  def show(self) -> None:
    Base.print(self.args)