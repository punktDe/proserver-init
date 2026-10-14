#!/usr/bin/env python3
import os
import argparse
from .infra import InfraScaffolding
from .constants import FROM_PATH
from importlib.metadata import version

def main():
    parser = argparse.ArgumentParser(prog='proserver-init', description='Initialize a Punkt.de project')
    parser.add_argument('-p', '--project-dir', type=str, help='path to the project', dest='project_dir', required=False, default=os.getcwd())
    parser.add_argument('-v', '--version', action='version', version=version('proserver-init'))
    parser.add_argument('--overlay', type=str, help='name of an overlay in ~/.config/proserver-init/overlays', dest='overlay', required=False, default=None)
    parser.add_argument('--overlay-path', type=str, help='path to an overlay directory', dest='overlay_path', required=False, default=None)
    subparsers = parser.add_subparsers(help='type of the project', dest='project_type', required=True)
    parser_infra = subparsers.add_parser('infra', help='')
    parser_infra.add_argument('-f', '--flavor', choices=InfraScaffolding.available_flavors(FROM_PATH), help='flavor of the project', required=False, default=None)
    parser_infra.add_argument('-a', '--app-identifier', type=str, help='name of the application, used for the role, its groups and its variables', dest='app_identifier', required=False, default='app')
    parser_infra.add_argument('--playbook-filename', type=str, help='file name of the generated playbook', dest='playbook_filename', required=False, default='playbook.yml')
    parser_infra_role = subparsers.add_parser('infra-role', help='')
    args = parser.parse_args()
    if args.project_type == "infra" and not "-infrastructure" in args.project_dir:
        raise parser.error("Infrastructure project folder should have an '-infrastructure' suffix")
    overlay_root = InfraScaffolding.resolve_overlay(args.overlay, args.overlay_path)
    if args.project_type == "infra":
        InfraScaffolding().init_project(from_path=FROM_PATH, to_path=args.project_dir, flavor=args.flavor,
                                        app_identifier=args.app_identifier, playbook_filename=args.playbook_filename,
                                        overlay_root=overlay_root)
    if args.project_type == "infra-role":
        InfraScaffolding().init_role(from_path=FROM_PATH, to_path=args.project_dir, overlay_root=overlay_root)
if __name__ == "__main__":
    main()
