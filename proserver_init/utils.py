from typing import Dict
from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError
from ruamel.yaml.parser import ParserError
import re
import shutil
import subprocess
import os
from rich import print
from .constants import INVENTORY_MARKER, APPEND_FILES, KEY_VALUE_EXTENSIONS
from .help_strings import direnv_not_installed

class Utils:
    yaml=YAML()
    yaml.explicit_start = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    # Without this, merging a file re-quotes every scalar in it, so the same
    # value comes out differently depending on whether a layer touched it.
    yaml.preserve_quotes = True


    @staticmethod
    def program_installed(exec_name: str, fail_if_not_installed: bool = False, fail_description: str = "") -> bool:
        result = subprocess.run(["which", exec_name], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        if result.returncode > 0:
            if len(fail_description) > 0:
                print(fail_description)
            if fail_if_not_installed:
                print(f":x: [red]ERROR:[/red] {exec_name} is not installed")
                exit(1)
            else:
                print(f":warning: [yellow]WARNING:[/yellow] {exec_name} is not installed")
                return False
        else: 
            return True

    @staticmethod
    def diff(file1, file2):
        Utils().program_installed("git", fail_if_not_installed=True)
        subprocess.run(["git", "diff", "--color-words", "--no-index", file1, file2])
            
    @staticmethod
    def project_post_init():
        subprocess.run("zsh .envrc && clear", shell=True)
        direnv_installed = Utils().program_installed("direnv", False, direnv_not_installed)
        if direnv_installed:
            subprocess.Popen("direnv allow", shell=True)
        Utils().program_installed("git", fail_if_not_installed=True)
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"])
        if not os.path.exists(".git/hooks/pre-commit"):
            subprocess.run(["pre-commit", "install"])
        subprocess.run(["pre-commit", "autoupdate"])


    def merge_dicts(self, dict1: Dict, dict2: Dict):
        try:
            merged_dict = dict1.copy()
        except AttributeError:
            merged_dict = {}
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

    def load_yaml(self, file_path: str):
        with open(file_path, 'r', encoding="utf-8") as f:
            return self.yaml.load(f)

    def merge_documents(self, base, flavor):
        '''
        Merges two parsed YAML documents. Mappings are merged key by
        key, sequences are appended to one another, and anything else
        is replaced by the later layer.
        '''
        if isinstance(base, dict) and isinstance(flavor, dict):
            return self.merge_dicts(base, flavor)
        if isinstance(base, list) and isinstance(flavor, list):
            merged = base.copy()
            merged.extend(flavor)
            return merged
        return flavor

    def append_yaml_sequences(self, base_file: str, flavor_file: str, dest_file: str) -> None:
        '''
        Appends one root level YAML sequence to another as text. Dumping
        the merged document would re-indent and re-wrap all of it, so the
        items are concatenated instead, which leaves comments, quoting
        and line breaks of both layers untouched.
        '''
        with open(base_file, 'r', encoding="utf-8") as f:
            base = f.read()
        with open(flavor_file, 'r', encoding="utf-8") as f:
            flavor_lines = f.readlines()
        while flavor_lines and flavor_lines[0].strip() in ("", "---"):
            flavor_lines.pop(0)
        if base and not base.endswith("\n"):
            base += "\n"
        if base and not base.endswith("\n\n"):
            base += "\n"
        with open(dest_file, 'w', encoding="utf-8") as f:
            f.write(base + "".join(flavor_lines))

    def merge_yaml(self, base_file: str, flavor_file: str, dest_file: str) -> None:
        try:
            base_yaml = self.load_yaml(base_file)
            flavor_yaml = self.load_yaml(flavor_file)
        except (ScannerError, ParserError) as error:
            print(f"[yellow]Warning![/yellow] {dest_file} could not be parsed as YAML "
                  f"({error.__class__.__name__}), so the later layer replaces it")
            shutil.copyfile(flavor_file, dest_file)
            return
        if isinstance(base_yaml, list) and isinstance(flavor_yaml, list):
            self.append_yaml_sequences(base_file, flavor_file, dest_file)
            return
        dest_yaml = self.merge_documents(base_yaml, flavor_yaml)
        with open(dest_file, 'w', encoding="utf-8") as f:
            self.yaml.dump(dest_yaml, f)

    def append_file(self, base_file: str, flavor_file: str, dest_file: str) -> None:
        '''
        Appends one layer's file to the layer below it. A later layer can
        lift part of its content higher up by marking it: everything above
        its INVENTORY_MARKER line is placed where the base has that marker,
        and the rest is appended. That is what lets a flavor add its hosts
        next to the other hosts while its groups stay at the bottom.
        '''
        with open(base_file, 'r', encoding="utf-8") as f:
            base = f.read()
        with open(flavor_file, 'r', encoding="utf-8") as f:
            flavor = f.read()
        if INVENTORY_MARKER in flavor:
            marked, flavor = flavor.split(INVENTORY_MARKER, 1)
            if INVENTORY_MARKER in base:
                base = base.replace(INVENTORY_MARKER,
                                    marked.strip("\n") + "\n\n" + INVENTORY_MARKER, 1)
            else:
                flavor = marked + flavor
        if base and not base.endswith("\n"):
            base += "\n"
        with open(dest_file, 'w', encoding="utf-8") as f:
            f.write(base + flavor)

    SECTION = re.compile(r"\s*\[(?P<name>.+)\]\s*$")
    SETTING = re.compile(r"\s*(?P<key>[^#;=\s][^=]*?)\s*=")

    def scan_settings(self, lines: list):
        '''
        Maps every (section, key) to the line that sets it, and every
        section to the line after its last setting.
        '''
        section = ""
        settings = {}
        ends = {"": 0}
        for index, line in enumerate(lines):
            match = self.SECTION.match(line)
            if match:
                section = match.group("name")
                ends[section] = index + 1
                continue
            if line.strip():
                ends[section] = index + 1
            match = self.SETTING.match(line)
            if match:
                settings[(section, match.group("key"))] = index
        return settings, ends

    def merge_key_values(self, base_file: str, flavor_file: str, dest_file: str) -> None:
        '''
        Merges a `key = value` config file setting by setting. A key the
        later layer sets replaces the same key in the same section below
        it, a new key is added to its section, and a section that is not
        there yet is appended. The lower layer keeps its comments and its
        order, so an overlay only has to carry the settings it changes.
        '''
        with open(base_file, 'r', encoding="utf-8") as f:
            base_lines = f.readlines()
        with open(flavor_file, 'r', encoding="utf-8") as f:
            flavor_lines = f.readlines()
        settings, ends = self.scan_settings(base_lines)
        replacements = {}
        insertions = {}
        appended = []
        section = ""
        for line in flavor_lines:
            if not line.endswith("\n"):
                line += "\n"
            match = self.SECTION.match(line)
            if match:
                section = match.group("name")
                if section not in ends:
                    appended.append(line)
                continue
            if section not in ends:
                appended.append(line)
                continue
            match = self.SETTING.match(line)
            if not match:
                continue
            key = match.group("key")
            if (section, key) in settings:
                replacements[settings[(section, key)]] = line
            else:
                insertions.setdefault(ends[section], []).append(line)
        merged = []
        for index, line in enumerate(base_lines):
            merged.extend(insertions.pop(index, []))
            merged.append(replacements.get(index, line))
        for index in sorted(insertions):
            merged.extend(insertions[index])
        merged.extend(appended)
        with open(dest_file, 'w', encoding="utf-8") as f:
            f.write("".join(merged))

    def merge_configs(self, base_file: str, flavor_file: str, dest_file: str) -> None:
        '''
        Merges one layer's file into the layer below it. YAML is merged
        document by document, inventories are appended so that a flavor
        can add host groups, and every other file is replaced outright
        by the later layer.

        Reads both inputs before writing, so the destination may be the
        same file as the base.
        '''
        effective_name = os.path.split(dest_file)[1].replace(".template", "")
        extension = os.path.splitext(effective_name)[1]
        if extension in (".yaml", ".yml"):
            self.merge_yaml(base_file, flavor_file, dest_file)
        elif extension == ".ini" or effective_name in APPEND_FILES:
            self.append_file(base_file, flavor_file, dest_file)
        elif extension in KEY_VALUE_EXTENSIONS:
            self.merge_key_values(base_file, flavor_file, dest_file)
        else:
            shutil.copy(flavor_file, dest_file)

    def protect_secret_file(self, file_path: str) -> None:
        '''
        Takes the group and world bits off a file holding a secret. An
        executable file is left alone: it is a script that fetches the
        secret from somewhere else rather than the secret itself.
        '''
        if os.path.exists(file_path) and not os.access(file_path, os.X_OK):
            os.chmod(file_path, 0o600)

    def match_permissions(self, src_file_path: str, dest_file_path: str) -> None:
        src_file_permissions = str(oct(os.stat(src_file_path).st_mode)[-3:])
        os.chmod(path = dest_file_path, mode = int(src_file_permissions, base=8))

    def create_project_structure(self, base_path: str, paths: list) -> None:
        for directory in paths:
            os.makedirs(os.path.join(base_path, directory), exist_ok=True)
