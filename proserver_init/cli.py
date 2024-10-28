#!/usr/bin/env python3
import os
import argparse
from .infra import InfraScaffolding
from .constants import FROM_PATH

def main():
    parser = argparse.ArgumentParser(prog='proserver-init', description='Initialize a Punkt.de project')
    parser.add_argument('-p', '--project-dir', type=str, help='path to the project', dest='project_dir', required=False, default=os.getcwd())
    subparsers = parser.add_subparsers(help='type of the project', dest='project_type', required=True)
    parser_infra = subparsers.add_parser('infra', help='')
    parser_infra.add_argument('-f', '--flavor', choices=('typo3', 'neos', 'spiral'), help='flavor of the project', required=False, default=None)
    parser_infra.add_argument('-p', '--project-dir', type=str, help='path to the project', required=False, default=os.getcwd())
    args = parser.parse_args()
    if args.project_type == "infra" and not "-infrastructure" in args.project_dir:
        raise parser.error("Infrastructure project folder should have an '-infrastructure' prefix")
    if args.project_type == "infra":
        InfraScaffolding().init_project(from_path=FROM_PATH, to_path=args.project_dir, flavor=args.flavor)


if __name__ == "__main__":
    main()
