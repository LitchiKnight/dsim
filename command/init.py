import os
import shutil
from git import Repo
from common.const import *
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
      self.create_dir(work_path)
      Utils.info(f"Create new work space for {project} at {work_path}")
      return True
    else:
      Utils.warning(f"{project} already exists at {work_path}")
      return False

  def pull_from_git(self) -> None:
    work_path = self.env["WORK_PATH"]
    repo_path = self.env["git_repo"]
    status, err_msg = self.run_cmd("git --version", mask=True)
    if status != CmdStatus.CMD_PASS:
      Utils.error("GIT is not installed")
    repo = Repo.init()
    remote = Utils.run_with_animation("Cloning remote repository", repo.clone_from, repo_path, work_path)
    Utils.info(f"Pull remote repository from {repo_path}")

  def pull_from_svn(self) -> None:
    work_path = self.env["WORK_PATH"]
    repo_path = self.env["svn_repo"]
    status, err_msg = self.run_cmd("svn --version", mask=True)
    if status != CmdStatus.CMD_PASS:
      Utils.error("SVN is not installed")
    os.chdir(work_path)
    status, err_msg = self.run_cmd(f"svn checkout {repo_path}")
    if status == CmdStatus.CMD_PASS:
      Utils.info(f"Pull remote repository from {repo_path}")
    else:
      Utils.error(err_msg)
    
  def pull_remote_repo(self) -> None:
    if self.args.ver_ctrl_sys == "git":
      self.pull_from_git()
    elif self.args.ver_ctrl_sys == "svn":
      self.pull_from_svn()

  def run(self) -> None:
    if self.init_work_path():
      if not self.args.no_pull:
        self.pull_remote_repo()