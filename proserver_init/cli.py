#!/usr/bin/env python3
import os
import argparse
from .infra import InfraScaffolding
from .constants import FROM_PATH

def main():
    parser = argparse.ArgumentParser(prog='proserver-init')
    parser.add_argument('--project_dir', type=str, help='Path of the project', required=False, default=os.getcwd())
    subparsers = parser.add_subparsers(help='type of the project', dest='project_type')
    parser_infra = subparsers.add_parser('infra', help='')
    parser_infra.add_argument('--flavor', choices=('typo3', 'neos', 'spiral'), help='flavor of the project', required=False, default=None)
    # create the parser for the "b" command
    args = parser.parse_args()
    if args.project_dir == FROM_PATH:
        raise parser.error(message=f"--project_dir cannot be equal to {FROM_PATH}")
    if args.project_type == "infra" and not "-infrastructure" in args.project_dir:
        raise parser.error("Infrastructure project folder should have an '-infrastructure' prefix")
    if args.project_type == "infra":
        InfraScaffolding().init_project(from_path=FROM_PATH, to_path=args.project_dir, flavor=args.flavor)


if __name__ == "__main__":
    main()
