#!/usr/bin/env python3
import os
from .utils import Utils
from .config_writer import ConfigWriter
from .utils import Utils
from .help_strings import infrastructure_success
from rich import print
import subprocess

class InfraScaffolding:
    def init_project(self, from_path, to_path, flavor = "generic"):
        utils = Utils()
        from_path = from_path / "templates" / "infra"
        directory_structure = [
                "group_vars",
                "roles/app/defaults",
                "roles/app/meta",
                "roles/app/tasks",
                "roles/app/templates",
                ]
        utils.create_project_structure(to_path, directory_structure)
        project_name = os.path.split(to_path)[1]
        project_organization = project_name.replace("-infrastructure", "")
        config = {
                "project_name": project_name,
                "project_organization": project_organization
                }
        ConfigWriter(from_path, to_path, config, flavor).write_configs()
        utils.direnv_allow()
        print(infrastructure_success.format(config['project_name']))
