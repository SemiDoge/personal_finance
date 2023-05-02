import yaml
import os

from .log import log, Log
from yaml.constructor import ConstructorError
from yaml.scanner import ScannerError
from yaml.parser import ParserError


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

        yaml.SafeLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, create_categorizer_yaml
        )

        with open(self.categorizer_path, "r") as f:
            try:
                categorizer = yaml.safe_load(f)
            except FileNotFoundError:
                log(Log.ERROR, f"Config file '{self.categorizer_path}' not found!")
                log(Log.WARNING, f"Using default categorizer. Continuing execution.")

                return default_categorizer
            except ParserError as error:
                log(
                    Log.ERROR,
                    f"Invalid YAML contained in config file '{self.categorizer_path}': {error.context} {error.problem} near [{error.context_mark.line}, {error.context_mark.column}]",
                )
                log(Log.WARNING, f"Using default categorizer. Continuing execution.")

                return default_categorizer
            except ScannerError as error:
                log(
                    Log.ERROR,
                    f"Invalid YAML contained in config file '{self.categorizer_path}': {error.context} {error.problem} near [{error.context_mark.line}, {error.context_mark.column}]",
                )
                log(Log.WARNING, f"Using default categorizer. Continuing execution.")

                return default_categorizer
            except ConstructorError as error:
                log(
                    Log.ERROR,
                    f"Invalid config file '{self.categorizer_path}' reason: {error}",
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


def create_categorizer_yaml(self, node):
    data = self.construct_mapping(node, deep=True)

    # test keys
    keys = list(data.keys())
    if len(keys) > 2:
        raise ConstructorError(f"{data} has too many keys")

    if "category" not in keys:
        raise ConstructorError(f"{data} is missing key 'category'")

    if "strings" not in keys:
        raise ConstructorError(f"{data} is missing key 'strings'")

    # test key types
    if isinstance(data, dict):
        if isinstance(data["category"], str):
            if isinstance(data["strings"], list):
                for string in data["strings"]:
                    if isinstance(string, str) == False:
                        raise ConstructorError(
                            f"Invalid data format ('{string}' ({type(string)}) does not match type {str})"
                        )
                    else:
                        continue

                return data
            else:
                raise ConstructorError(
                    f"Invalid data format ('{data['strings']}' ({type(data['strings'])}) does not match type {list})"
                )
        else:
            raise ConstructorError(
                f"Invalid data format ('{data['category']}' ({type(data['category'])}) does not match type {str})"
            )
    else:
        raise ConstructorError(
            f"Invalid data format ('{data}' ({type(data)}) does not match type {dict})"
        )
