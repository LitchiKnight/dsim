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
    project = self.args.project
    work_path = self.env["WORK_PATH"]
    if self.args.force:
      shutil.rmtree(work_path, ignore_errors=True)
      if os.path.exists(work_path):
        Utils.error(f"Unable to remove {project} project")
      Utils.info(f"Deleted {project} existing work space")
    if not os.path.exists(work_path):
      os.makedirs(work_path)
      Utils.info(f"Create new work space for {project} at {work_path}")
      return True
    else:
      Utils.warning(f"{project} already exists at {work_path}")
      return False

  def pull_from_git(self) -> None:
    work_path = self.env["WORK_PATH"]
    repo_path = self.env["git_repo"]
    try:
      subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
      Utils.error("GIT is not installed")
    repo = Repo.init()
    remote = Utils.run_with_animation("Cloning remote repository", repo.clone_from, repo_path, work_path)
    Utils.info(f"Pull remote repository from {repo_path}")

  def pull_from_svn(self) -> None:
    repo_path = self.env["git_svn"]
    try:
      subprocess.run(["svn", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
      Utils.error("SVN is not installed")
    Utils.info(f"Pull remote repository from {repo_path}")
    
  def pull_remote_repo(self) -> None:
    if self.args.VCS == "git":
      self.pull_from_git()
    elif self.args.VCS == "svn":
      self.pull_from_svn()

  def run(self) -> None:
    if self.init_work_path():
      if not self.args.no_pull:
        self.pull_remote_repo()