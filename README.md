# proserver-init

A command-line utility that facilitates setting up a new punkt.de Proserver project

## Dependencies

- homebrew
- direnv (optional)

## Installation

```bash
brew tap pt/proserver-init https://github.com/punktDe/proserver-init.git
brew install proserver-init
brew install --HEAD proserver-init # to install the development version
```

Alternatively, run as a Nix flake, e.g.:

```bash
nix run github:punktDe/proserver-init <parameters>
```

## Usage

```bash
proserver-init [--project_dir/-p path/to/project] project-type [--flavor/-f flavor]

# Set up a generic Ansible project in the current directory
proserver-init infra

# Set up a Neos infrastructure project in ~/Workspace/Project/example-infrastructure
proserver-init -p ~/Workspace/Projects/example-infrastucture infra -f neos
```

Available project types:

- infra
- infra-role

Available flavors:

- typo3
- neos
- spiral
