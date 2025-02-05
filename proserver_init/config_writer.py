from pathlib import Path
import os
from string import Template
from .utils import Utils
from filecmp import cmp
from rich import print

class ConfigWriter:

    def __init__(self, from_path: Path, to_path: str, config: dict, flavor=None):
        self.utils = Utils()
        self.from_path = from_path
        self.to_path = to_path
        self.config = config
        self.flavor = flavor

    def write_config(self, from_path: str, dest_path: str) -> None:
        '''
        Copies/templates the config to the target folder.
        Checks if the config with the same already exists
        in the target folder and gives the user
        an option to overwrite or skip the file.
        '''
        print(f"[bright_black]Templated {dest_path}[/bright_black]")
        with open(from_path, "r", encoding="utf-8") as ffile:
            if "template" in os.path.split(from_path)[1]:
                dest_path = dest_path.replace(".template", "")
                from_file_template = Template(ffile.read())
                from_file = from_file_template.substitute(self.config)
            else:
                from_file = ffile.read()
        if os.path.exists(dest_path):
            tmp_file = os.path.join(os.path.split(dest_path)[0], "." + os.path.split(dest_path)[1] + ".tmp")
            with open(tmp_file, 'w') as f:
                f.write(from_file)
            if cmp(tmp_file, dest_path, shallow=False):
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                return
            else:
                while True:
                    print(f"Replace the file {dest_path}? (yes/no/diff)")
                    replace = input()
                    if replace == "no":
                        if os.path.exists(tmp_file):
                            os.remove(tmp_file)
                        return
                    if replace == "yes":
                        break
                    elif replace == "diff":
                        self.utils.diff(dest_path, tmp_file)
                    else:
                        print("Please type either 'yes', 'no' or 'diff'")
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
        with open(dest_path, "w+", encoding="utf-8") as dfile:
            dfile.write(from_file)
        self.utils.match_permissions(from_path, dest_path)
        
    def write_configs(self):
        '''
        Writes all configs from the template folder
        to the target project folder.

        If a flavor is selected, merges the 'generic'
        templates/configs with the 'flavored' 
        templates/configs, and writem to the target
        project folder.
        '''
        from_root = self.from_path / "generic"
        dest_paths = []
        flavor_root = ""
        flavor_files = []
        if isinstance(self.flavor, str):
            flavor_root = os.path.join(self.from_path, self.flavor)
            flavor_files = [os.path.join(dp, f) for dp, _, filenames in os.walk(flavor_root) for f in filenames]
        for root, _, files in os.walk(from_root):
            for file in files:
                if os.path.splitext(file)[1] == ".pyc":
                    continue
                from_file = os.path.join(root, file)
                relative_file_path = os.path.relpath(from_file, start=from_root)
                dest_file = os.path.join(self.to_path, relative_file_path)
                dest_path = os.path.split(dest_file)[0]
                if not dest_path in dest_paths:
                    dest_paths.append(dest_path)
                    os.makedirs(dest_path, exist_ok=True)
                if isinstance(self.flavor, str):
                    flavor_file = os.path.join(flavor_root, relative_file_path)
                    if flavor_file in flavor_files:
                        self.utils.merge_configs(base_file=from_file, flavor_file=flavor_file, dest_file = dest_file)
                        continue
                self.write_config(from_file, dest_file)
