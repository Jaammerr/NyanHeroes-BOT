import os

import yaml
from loguru import logger

from models import Account, Config


def get_accounts() -> Account:
    accounts_path = os.path.join(os.path.dirname(__file__), "accounts.txt")
    if os.path.exists(accounts_path):
        with open(accounts_path, "r") as f:
            accounts = f.read().splitlines()

        if not accounts:
            logger.error("No accounts found in config/accounts.txt")
            exit(1)

        for account in accounts:
            values = account.split("|")
            if len(values) == 1:
                yield Account(auth_token=account)

            elif len(values) == 2:
                if ":" in values[1]:
                    yield Account(auth_token=values[0], proxy=values[1])
                else:
                    yield Account(auth_token=values[0], mnemonic=values[1])

            elif len(values) == 3:
                yield Account(auth_token=values[0], mnemonic=values[1], proxy=values[2])

    else:
        logger.error("No accounts found in config/accounts.txt")
        exit(1)


def load_config() -> Config:
    settings_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
    if os.path.exists(settings_path):
        with open(settings_path, "r") as f:
            settings = yaml.safe_load(f)

        if not settings.get("timeout_between_quests"):
            logger.error("No timeout_between_quests found in config/settings.yaml")
            exit(1)

        if not settings.get("threads"):
            logger.error("No threads found in config/settings.yaml")
            exit(1)

        if not settings.get("ignored_quests_categories"):
            logger.error("No ignored_quests_categories found in config/settings.yaml")
            exit(1)

        if not settings.get("referral_code"):
            logger.error("No referral_code found in config/settings.yaml")
            exit(1)

        accounts = list(get_accounts())
        return Config(**settings, accounts=accounts)

    else:
        logger.error("No settings found in config/settings.yaml")
        exit(1)
