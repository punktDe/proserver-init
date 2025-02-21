from pathlib import Path
import os
from string import Template
from .utils import Utils
from filecmp import cmp
from rich import print
import tempfile
import shutil

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
            never_replace = ["roles/app", "host_vars", "group_vars", "requirements.yml", "README.md", "inventory.ini", "vault_password_file"] 
            if cmp(tmp_file, dest_path, shallow=False) or any(pattern in dest_path for pattern in never_replace):
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
            print(f"[bright_black]Templated {dest_path}[/bright_black]")
        self.utils.match_permissions(from_path, dest_path)
        
    def write_configs(self):
        '''
        Writes all configs from the template folder
        to the target project folder.

        If a flavor is selected, merges the 'generic'
        templates/configs with the 'flavored' 
        templates/configs, and writes them to the target
        project folder.
        '''
        from_root = self.from_path / "generic"
        dest_paths = []
        flavor_root = ""
        flavor_files = []
        merged_from_root = tempfile.TemporaryDirectory().name
        if isinstance(self.flavor, str):
            flavor_root = os.path.join(self.from_path, self.flavor)
            flavor_files = [os.path.join(dp, f) for dp, _, filenames in os.walk(flavor_root) for f in filenames]
            from_files = [os.path.join(dp, f) for dp, _, filenames in os.walk(from_root) for f in filenames]
            unflavored_files = [file for file in from_files if os.path.relpath(file, start=from_root) not in [os.path.relpath(ffile, start=flavor_root) for ffile in flavor_files]]
            os.mkdir(merged_from_root)
            for ufile in unflavored_files:
                dest_file = str(os.path.join(merged_from_root, str(os.path.relpath(ufile, start=from_root))))
                dest_path = os.path.split(dest_file)[0]
                os.makedirs(dest_path, exist_ok=True)
                shutil.copy(ufile, dest_file)
            for flavor_file in flavor_files:
                relative_file_path = os.path.relpath(flavor_file, start=flavor_root)
                dest_file = os.path.join(merged_from_root, relative_file_path)
                base_file = os.path.join(from_root, relative_file_path)
                if not os.path.exists(base_file):
                    _, base_file = tempfile.mkstemp()
                dest_path = os.path.split(dest_file)[0]
                os.makedirs(dest_path, exist_ok=True)
                self.utils.merge_configs(base_file=base_file, flavor_file=flavor_file, dest_file=dest_file)
            from_root = merged_from_root
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
                self.write_config(from_file, dest_file)
        if os.path.exists(merged_from_root):
            shutil.rmtree(merged_from_root)
