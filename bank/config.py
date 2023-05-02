import yaml
import os

from .log import log, Log


class Configuration:
    def __init__(self, config_dir: str):
        self.categorizer_path = f"{config_dir}/categorizer.yaml"
        self.categorizer = self.load_categorizer_config()

    def load_categorizer_config(self):
        default_categorizer = [
            {"category": "Subscriptions", "strings": ["RECURRING"]},
            {"category": "Refunds", "strings": ["REFUND"]},
            {
                "category": "Government/Taxes",
                "strings": ["CANADA ", " GST", " PRO", " FED", "CRA", "GOV CA"],
            },
            {"category": "Transfers", "strings": ["ETRNSFR", "RECVD", "TF "]},
            {"category": "Online/Others", "strings": ["ONLINE"]},
        ]

        try:
            with open(self.categorizer_path, "r") as f:
                categorizer = yaml.load(f, Loader=yaml.SafeLoader)
        except FileNotFoundError:
            log(Log.ERROR, f"Config file '{self.categorizer_path}' not found!")
            log(Log.WARNING, f"Using default categorizer. Continuing execution.")

            return default_categorizer
        except yaml.scanner.ScannerError as error:
            log(
                Log.ERROR,
                f"Invalid YAML contained in config file '{self.categorizer_path}': {error.context} {error.problem} near [{error.context_mark.line}, {error.context_mark.column}]",
            )
            log(Log.WARNING, f"Using default categorizer. Continuing execution.")

            return default_categorizer
        except PermissionError:
            log(
                Log.ERROR,
                f"User '{os.getlogin()}' does not have permissions to access file '{self.categorizer_path}'",
            )
            log(Log.WARNING, f"Using default categorizer. Continuing execution.")

            return default_categorizer

        return categorizer

    def get_categorizer(self):
        return self.categorizer
