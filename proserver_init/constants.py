import importlib.resources as importlib_resources
import os
from pathlib import Path

FROM_PATH = importlib_resources.files("proserver_init")

VALUES_FILE = "values.yaml"

# Marks where a later layer's hosts go in an inventory, so that a flavor
# can add its hosts next to the others instead of below its own groups.
INVENTORY_MARKER = "#@hosts"

# Line based files, where a later layer adds to what is below it rather
# than replacing the file.
APPEND_FILES = (".gitignore", ".gitattributes", ".dockerignore")

# `key = value` files, merged setting by setting.
KEY_VALUE_EXTENSIONS = (".cfg",)

CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "proserver-init"

OVERLAY_HOME = CONFIG_HOME / "overlays"
