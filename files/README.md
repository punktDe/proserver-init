# {1}

### Preparing your system
```sh
brew install direnv bitwarden-cli pre-commit
bw config server pass.punkt.de
bw login
echo 'export BW_SESSION="your-session-key" >> ~/.zshrc'
source ~/.zshrc
```

### Cloning the repository
```sh
git clone git@git.punkt.de:{0}/{1}.git ~/Workspace/Projects/{1}
cd ~/Workspace/Projects/{1}
```

### Installing the dependencies
```sh
direnv allow
```

### Enabling linting and pre-commit checks
```sh
pre-commit install
```

### Run Ansible playbook
```sh
ansible-playbook {0}.yaml --limit staging

