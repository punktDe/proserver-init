# proserver-init
A command-line utility that facilitates setting up a new Punkt.de project.

# Dependencies
* homebrew
* direnv (optional)

# Installation
```
brew tap pt/proserver-init git@git.punkt.de:pt/proserver-init.git
brew install proserver-init
```

# Usage
```
proserver-init [--project_dir path/to/project] project_type [--flavor flavor]

# Set up a generic Ansible project in the current directory
proserver-init infra

# Set up a Neos infrastructure project in ~/Workspace/Project/example-infrastructure
proserver-init --project_dir ~/Workspace/Projects/example-infrastucture infra --flavor neos
```

Available project types:
* infra

Available flavors:
* typo3
* neos
* spiral
