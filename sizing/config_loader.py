import yaml

from sizing.models import TransactionProfile, SizingDefaults


def load_config(path: str):
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    profiles = {
        name: TransactionProfile(name=name, **fields)
        for name, fields in raw["transaction_types"].items()
    }
    defaults = SizingDefaults(**raw["defaults"])

    return profiles, defaults
