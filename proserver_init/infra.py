#!/usr/bin/env python3
import os
import secrets
from pathlib import Path
from .utils import Utils
from .config_writer import ConfigWriter
from .constants import OVERLAY_HOME
from .help_strings import infrastructure_success
from rich import print

class InfraScaffolding:
    def __init__(self):
        self.utils = Utils()

    @staticmethod
    def available_flavors(from_path) -> tuple:
        '''
        Lists the flavors that have a template directory,
        so that the CLI never offers a flavor which would
        silently fall back to the generic templates.
        '''
        flavors_path = from_path / "templates" / "infra"
        return tuple(sorted(entry.name for entry in flavors_path.iterdir()
                            if entry.is_dir() and entry.name != "generic"))

    @staticmethod
    def resolve_overlay(overlay: str = None, overlay_path: str = None) -> str:
        '''
        Turns the overlay arguments into a directory. An overlay name
        is looked up in ~/.config/proserver-init/overlays, a path is
        taken as given.
        '''
        if overlay_path:
            resolved = Path(overlay_path).expanduser()
        elif overlay:
            resolved = OVERLAY_HOME / overlay
        else:
            return None
        if not resolved.is_dir():
            print(f":x: [red]ERROR:[/red] Overlay directory {resolved} does not exist")
            exit(1)
        return str(resolved)

    def layer_paths(self, from_path, templates_dir: str, flavor: str = None, overlay_root: str = None) -> list:
        '''
        Builds the layer chain: the public generic templates, the
        public flavor on top of them, and then the same two levels
        from the overlay. Overlay layers are optional, so an overlay
        only has to carry the levels it actually changes.
        '''
        templates_root = from_path / "templates" / templates_dir
        layers = [templates_root / "generic"]
        if flavor:
            flavor_root = templates_root / flavor
            if not os.path.isdir(str(flavor_root)):
                print(f":x: [red]ERROR:[/red] No templates found for the flavor '{flavor}'")
                exit(1)
            layers.append(flavor_root)
        if overlay_root:
            overlay_layers = [Path(overlay_root) / templates_dir / "generic"]
            if flavor:
                overlay_layers.append(Path(overlay_root) / templates_dir / flavor)
            layers.extend(layer for layer in overlay_layers if os.path.isdir(str(layer)))
        return layers

    def init_project(self, from_path, to_path, flavor = None, app_identifier = "app",
                     playbook_filename = "playbook.yaml", overlay_root = None):
        project_name = os.path.split(to_path)[1]
        project_organization = project_name.replace("-infrastructure", "")
        config = {
                "project_name": project_name,
                "project_organization": project_organization,
                "app_identifier": app_identifier,
                "app_identifier_title": app_identifier.capitalize(),
                "playbook_filename": playbook_filename,
                "vault_password": secrets.token_urlsafe(32),
                }
        layers = self.layer_paths(from_path, "infra", flavor, overlay_root)
        ConfigWriter(layers, to_path, config).write_configs()
        self.utils.protect_secret_file(os.path.join(to_path, "vault_password_file"))
        os.chdir(to_path)
        self.utils.project_post_init()
        print(infrastructure_success.format(config['project_name']))

    def init_role(self, from_path, to_path, overlay_root = None):
        directory_structure = [
                "defaults",
                "handlers",
                "meta",
                "tasks",
                "templates",
                ]
        self.utils.create_project_structure(to_path, directory_structure)
        role_name = os.path.split(to_path)[1]
        config = {
                "role_name": role_name,
                "role_name_short": role_name.removeprefix("ansible-proserver-").removeprefix("ansible-")
                }
        layers = self.layer_paths(from_path, "infra_role", None, overlay_root)
        ConfigWriter(layers, to_path, config).write_configs()
        os.chdir(to_path)
        self.utils.project_post_init()
        print(f"{role_name} has been initialized succesfully")
