from .utils import Utils
import importlib.resources as importlib_resources

application_support_dir = Utils().find_application_support_dir()
FROM_PATH = importlib_resources.files("proserver_init")
