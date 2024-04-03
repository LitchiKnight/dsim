import os
import yaml
import getpass
from common.utils import Utils

class Config:
  def __init__(self) -> None:
    pass

  @property
  def yaml_path(self) -> str:
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(os.path.dirname(curr_dir), "yaml")

  def get_env(self, project: str) -> dict:
    yaml_file = os.path.join(self.yaml_path, "env.yaml")
    try:
      with open(yaml_file, mode="r", encoding="utf-8") as f:
        temp = f.read().strip()
        content = temp.replace("<user>", getpass.getuser())
        env = yaml.load(content, Loader=yaml.FullLoader)
    except Exception as e:
      Utils.error(e)
    for item in env:
      if project in item:
        return item[project]
    Utils.error(f"No such project: {project}")

  def get_work_dir(self, module: str) -> dict:
    yaml_file = os.path.join(self.yaml_path, "template.yaml")
    try:
      with open(yaml_file, mode="r", encoding="utf-8") as f:
        temp = f.read().strip()
        content = temp.replace("<module>", module)
        template = yaml.load(content, Loader=yaml.FullLoader)
    except Exception as e:
      Utils.error(e)
    for item in template:
      if "work_dir" in item:
        return item["work_dir"]
    Utils.error("No such template: work_dir")

  def get_simulator_cmd(self, tool: str) -> dict:
    yaml_file = os.path.join(self.yaml_path, "simulator.yaml")
    try:
      with open(yaml_file, mode="r", encoding="utf-8") as f:
        content = f.read().strip()
        simulator = yaml.load(content, Loader=yaml.FullLoader)
    except Exception as e:
      Utils.error(e)
    for item in simulator:
      if tool in item:
        return item[tool]
    Utils.error(f"No such simulator: {tool}")