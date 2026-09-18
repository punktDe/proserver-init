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
proserver-init [--project-dir/-p path/to/project] project-type [options]

# Set up a generic Ansible project in the current directory
proserver-init infra

# Set up a TYPO3 infrastructure project in ~/Workspace/Projects/example-infrastructure
proserver-init -p ~/Workspace/Projects/example-infrastructure infra -f typo3

# Name the application "shop" instead of "app"
proserver-init infra -f typo3 --app-identifier shop
```

Available project types:

- infra
- infra-role

Available flavors:

- typo3
- neos

The flavor list is read from the template directory, so a flavor is offered
exactly when templates exist for it.

### Options for `infra`

| Option | Default | Effect |
| --- | --- | --- |
| `-f`, `--flavor` | none | Application stack to layer on top of the generic templates |
| `-a`, `--app-identifier` | `app` | Name of the application |
| `--playbook-filename` | `playbook.yaml` | File name of the generated playbook |

The app identifier names the application everywhere it appears on disk and in
the inventory: the role in `roles/<identifier>`, the inventory groups
`<identifier>`, `<identifier>_stg` and `<identifier>_prd`, the matching files in
`group_vars` and `host_vars`, the nginx site, the `.env` file and the deployment
directory under `/var/www`.

The role's own Ansible variables stay under the `app` key regardless of the
identifier, so `app.domain` and `app.config` mean the same thing in every
generated project. This keeps the nginx vhost template free of substitution
markers, which matters because it is full of `$`-prefixed nginx variables.

## Template layers

Templates are applied in layers, and each layer only carries its own deltas:

```
templates/infra/generic  ->  templates/infra/<flavor>  ->  <overlay>/infra/generic  ->  <overlay>/infra/<flavor>
```

How a later layer combines with the one below it depends on the file:

| Content | Rule |
| --- | --- |
| `.yaml` / `.yml` mapping | merged key by key |
| `.yaml` / `.yml` sequence | appended, as text, so formatting and comments survive |
| `.ini` | appended, which is how a flavor adds inventory groups |
| `.ini` above a `#@hosts` line | placed where the layer below has its own `#@hosts` line |
| anything else | replaced by the later layer |
| a file only the later layer has | copied in as it is |

### Template conventions

- `$variable` and `${variable}` in a **path** are substituted, so a template at
  `roles/$app_identifier/tasks/main.yaml` lands under the name the project uses.
  Use the braced form before an underscore: `${app_identifier}_prd.yaml`.
- A file whose name contains `template` also has its **contents** substituted,
  and loses the `.template` suffix on the way out.
- A file must be named the same way in every layer, `.template` suffix included.
  Two layers disagreeing about the suffix produce two files that overwrite each
  other instead of merging.
- `values.yaml` at the root of a layer is not copied into the project. It
  supplies substitution values, and a later layer overrides them.
- A `#@hosts` line marks where a later layer's inventory hosts go. Content
  above a flavor's own `#@hosts` line is placed there rather than appended, so
  a flavor's hosts sit with the other hosts while its groups stay at the
  bottom. The markers are removed from the generated file.

## Overlays

An overlay adds organization-specific defaults to the public templates without
forking them. It mirrors the template layout and holds only the deltas:

```
my-overlay/
  infra/generic/values.yaml            # substitution values
  infra/generic/ansible.cfg            # replaces the public one
  infra/generic/inventory.py           # a file the public templates do not have
  infra/generic/group_vars/all.yaml    # merged into the public group_vars/all.yaml
  infra/typo3/group_vars/${app_identifier}.yaml.template
```

Point at one by path, or by name if it lives in `~/.config/proserver-init/overlays`:

```bash
proserver-init --overlay-path ~/src/my-overlay infra -f typo3
proserver-init --overlay my-overlay infra -f typo3
```

The public templates ship no organization-specific values: the identity
provider, the git remote and the DNS suffix are empty or example values, no CI
configuration is generated, and no particular secrets manager is assumed.

### The Ansible Vault password

A generated project gets a random Ansible Vault password written into
`vault_password_file`, which is git-ignored and readable only by its owner.

An overlay that reads the password from a secrets manager replaces that file
with an executable script printing the password on stdout, and overrides the
`brew_packages` and `vault_password_instructions` values so that the generated
README documents its own setup. Ansible runs `vault_password_file` when it is
executable and reads it as a password otherwise, so the two work the same way
from the playbook's side.
