from pydantic import BaseModel, PositiveInt
from .account import Account


class Config(BaseModel):
    accounts: list[Account]
    timeout_between_quests: PositiveInt
    ignored_quests_categories: list[str]
    referral_code: str
    threads: PositiveInt
