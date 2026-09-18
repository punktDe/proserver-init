infrastructure_success = """
:sparkles: [green]Success! Infrastructure project[/green] [bold green]{}[/bold green] [green]has been initialized.[/green]

* A random Ansible Vault password was generated into `vault_password_file`.
  That file is git-ignored. Share the password through your team's secrets manager,
  and have every contributor put it there before running Ansible.

  To read the password from a secrets manager instead, replace the file with an
  executable script that prints the password on stdout.

* Fill in `group_vars/secrets.yaml` and encrypt it before committing:
  `ansible-vault encrypt group_vars/secrets.yaml`
"""

direnv_not_installed = f"""
:warning: [yellow]Warning![/yellow] direnv is not installed. In order to automatically activate 
the Python virtual environment and export necessary environment variables when entering this 
project's directory, please install direnv via Homebrew, MacPorts or Nix.

Alternatively, run `source .envrc` upon entering the project directory.
"""
