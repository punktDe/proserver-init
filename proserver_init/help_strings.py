infrastructure_success = """
:sparkles: [green]Success! Infrastructure project[/green] [bold green]{}[/bold green] [green]has been initialized.[/green]

* Please make sure to update your `vault_password_file` before creating your secrets.yaml file.
  By default, the script fetches the Ansible Vault password from a Bitwarden vault.
  Make sure to add the actual name of your Vault password entry to the vault_password_file.

  If you choose to store your Vault password in cleartext instead of using a secrets manager,
  make sure to remove the executable bit from the vault_password_file: `chmod -x vault_password_file`
"""
