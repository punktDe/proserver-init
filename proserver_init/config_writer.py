import os
from string import Template
from .utils import Utils
from .constants import VALUES_FILE
from filecmp import cmp
from rich import print
import tempfile
import shutil

class ConfigWriter:

    def __init__(self, layer_paths: list, to_path: str, config: dict):
        self.utils = Utils()
        self.layer_paths = [str(layer_path) for layer_path in layer_paths]
        self.to_path = to_path
        self.config = {**self.read_values(), **config}

    def read_values(self) -> dict:
        '''
        Collects the substitution values every layer contributes.
        A later layer overrides the values of the layers below it,
        which is how an overlay replaces a default without having
        to restate the file that uses it.
        '''
        values = {}
        for layer_path in self.layer_paths:
            values_file = os.path.join(layer_path, VALUES_FILE)
            if os.path.exists(values_file):
                values.update(self.utils.load_yaml(values_file) or {})
        return values

    def merge_layers(self) -> str:
        '''
        Folds the layers into a single tree in a temporary directory.
        The first layer is copied, every later one is merged into the
        result so far, so that each layer only has to carry its deltas.
        '''
        merged_root = tempfile.mkdtemp(prefix="proserver-init-")
        for layer_path in self.layer_paths:
            self.apply_layer(layer_path, merged_root)
        return merged_root

    def apply_layer(self, layer_path: str, merged_root: str) -> None:
        for root, _, files in os.walk(layer_path):
            for file in files:
                if os.path.splitext(file)[1] == ".pyc":
                    continue
                from_file = os.path.join(root, file)
                relative_file_path = os.path.relpath(from_file, start=layer_path)
                if relative_file_path == VALUES_FILE:
                    continue
                dest_file = os.path.join(merged_root, self.substitute_path(relative_file_path))
                os.makedirs(os.path.split(dest_file)[0], exist_ok=True)
                if os.path.exists(dest_file):
                    self.utils.merge_configs(base_file=dest_file, flavor_file=from_file, dest_file=dest_file)
                else:
                    shutil.copy(from_file, dest_file)

    def substitute_path(self, relative_file_path: str) -> str:
        '''
        Substitutes the configuration into the path itself, so that a
        template can live at roles/$app_identifier/tasks/main.yaml and
        land under the name the project actually uses. Applied while the
        layers are merged, so that two layers naming the same file agree
        on it and the merge rule sees the final extension.
        '''
        return Template(relative_file_path).substitute(self.config)

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
            never_replace = ["roles/" + self.config.get("app_identifier", "app"), "host_vars", "group_vars", "requirements.yml", "requirements.yaml", "README.md", "inventory.ini", "vault_password_file"] 
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
        Merges every layer into one tree and writes it to the target
        project folder, substituting the configuration into both the
        file contents and the paths.
        '''
        merged_root = self.merge_layers()
        dest_paths = []
        try:
            for root, _, files in os.walk(merged_root):
                for file in files:
                    from_file = os.path.join(root, file)
                    relative_file_path = os.path.relpath(from_file, start=merged_root)
                    dest_file = os.path.join(self.to_path, relative_file_path)
                    dest_path = os.path.split(dest_file)[0]
                    if not dest_path in dest_paths:
                        dest_paths.append(dest_path)
                        os.makedirs(dest_path, exist_ok=True)
                    self.write_config(from_file, dest_file)
        finally:
            shutil.rmtree(merged_root, ignore_errors=True)
