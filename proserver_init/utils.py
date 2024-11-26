import re
from typing import Dict
from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError
from ruamel.yaml.parser import ParserError
import subprocess
import os
from rich import print
from .help_strings import command_not_installed

class Utils:
    yaml=YAML()
    yaml.explicit_start = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    @staticmethod
    def diff(file1, file2):
        git_installed = subprocess.run(["which", "git"], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        if git_installed.returncode > 0:
            print("ERROR: git not installed")
            exit(1)
        subprocess.run(["git", "diff", "--color-words", "--no-index", file1, file2])
            
    @staticmethod
    def direnv_allow():
        subprocess.run("zsh .envrc && clear", shell=True)
        direnv_installed = subprocess.run(["which", "direnv"], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        if direnv_installed.returncode > 0:
            print(command_not_installed)
        else:
            subprocess.Popen("direnv allow", shell=True)

    def merge_dicts(self, dict1: Dict, dict2: Dict):
        merged_dict = dict1.copy()
        for key, value in dict2.items():
            if key in merged_dict:
                if isinstance(merged_dict[key], dict) and isinstance(value, dict):
                    merged_dict[key] = self.merge_dicts(merged_dict[key], value)
                elif isinstance(merged_dict[key], list) and isinstance(value, list):
                    merged_dict[key].extend(value)
                else:
                    merged_dict[key] = value
            else:
                merged_dict[key] = value
        return merged_dict

    def merge_yaml(self, base_file: str, flavor_file: str, dest_file: str) -> None:
        with open(base_file, 'r', encoding="utf-8") as f:
            base_yaml = self.yaml.load(f)
        with open(flavor_file, 'r', encoding="utf-8") as f:
            flavor_yaml = self.yaml.load(f)
        dest_yaml = self.merge_dicts(base_yaml, flavor_yaml)
        with open(dest_file, 'w+', encoding="utf-8") as f:
            self.yaml.dump(dest_yaml, f)

    def merge_configs(self, base_file: str, flavor_file: str, dest_file: str) -> None:
        try:
            self.merge_yaml(base_file, flavor_file, dest_file)
            return
        except (ScannerError, AttributeError, ParserError):
            for filename in [base_file, flavor_file, dest_file]:
                if re.search(r"ya?ml", filename) and not "template" in filename:
                    print(f"[yellow]Warning![/yellow] File {filename} is not a valid YAML file!")
        with open(base_file, 'r', encoding="utf-8") as bfile, \
             open(flavor_file, 'r', encoding="utf-8") as ffile, \
             open(dest_file, 'w+', encoding="utf-8") as dfile:
            for line in (bfile.readlines() + ffile.readlines()):
                dfile.write(line)

    def match_permissions(self, src_file_path: str, dest_file_path: str) -> None:
        src_file_permissions = str(oct(os.stat(src_file_path).st_mode)[-3:])
        os.chmod(path = dest_file_path, mode = int(src_file_permissions, base=8))

    def create_project_structure(self, base_path: str, paths: list) -> None:
        for directory in paths:
            os.makedirs(os.path.join(base_path, directory), exist_ok=True)

    def find_application_support_dir(self):
        windows = r"%APPDATA%"
        windows = os.path.expandvars(windows)
        if 'APPDATA' not in windows:
            return windows
        user_directory = os.path.expanduser('~')
        macos = os.path.join(user_directory, 'Library', 'Application Support')
        if os.path.exists(macos):
            return macos
        linux = os.path.join(user_directory, '.local', 'share')
        if os.path.exists(linux):
            return linux
        return user_directory
