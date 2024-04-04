import asyncio
import os

import aiofiles
import noble_tls
import pyuseragents
import names

from typing import Literal
from loguru import logger

from twitter_api import Account as TwitterAccount
from twitter_api.models import BindAccountParamsV1

from .exceptions import APIError
from .utils import *
from .wallet import Wallet

from models import Account
from loader import config


class Bot(noble_tls.Session):
    API_URL = "https://api.nyanheroes.com"

    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.wallet = Wallet(self.account.mnemonic)
        self.setup_session()

    def setup_session(self) -> None:
        self.client_identifier = "chrome_120"
        self.random_tls_extension_order = True

        if self.account.proxy:
            self.proxies = {"http": self.account.proxy, "https": self.account.proxy}
        self.headers = {
            "authority": "api.nyanheroes.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "fr-FR,fr;q=0.9",
            "content-type": "application/json",
            "origin": "https://missions.nyanheroes.com",
            "user-agent": pyuseragents.random(),
        }

    async def bind_wallet(self) -> None:
        try:
            signature_data = self.wallet.sign_message()

            json_data = {
                "QuestId": 2,
                "WalletAddress": self.wallet.get_address,
                "Signature": str(signature_data.signature),
                "Message": signature_data.message,
                "IsLedger": False,
            }

            await self.send_request(method="/Quest/verifyMessage", json_data=json_data)
            logger.success(
                f"Account: {self.account.auth_token} | Completed quest: Bind Wallet | Category: wallet"
            )

        except Exception as error:
            logger.error(
                f"Account: {self.account.auth_token} | Failed to complete quest: Bind Wallet | Category: wallet | Error: {error}"
            )

    async def send_request(
        self,
        request_type: Literal["POST", "GET"] = "POST",
        method: str = None,
        json_data: dict = None,
        params: dict = None,
        url: str = None,
    ):

        def _verify_response(_response: dict) -> dict:
            if "result" in _response:
                if not _response["result"]:
                    raise APIError(
                        f"{_response.get('error')} | Method: {method}"
                    )

            return _response

        if request_type == "POST":
            if not url:
                response = await self.post(
                    f"{self.API_URL}{method}", json=json_data, params=params
                )

            else:
                response = await self.post(url, json=json_data, params=params)

        else:
            if not url:
                response = await self.get(f"{self.API_URL}{method}", params=params)

            else:
                response = await self.get(url, params=params)

        if response.status_code == 429:
            logger.error(
                f"Account: {self.account.auth_token} | Rate limited | Method: {method} | Retrying in 3 seconds..."
            )
            await asyncio.sleep(3)
            return await self.send_request(request_type, method, json_data, params, url)

        response.raise_for_status()
        return _verify_response(response.json())

    async def login(self) -> bool:
        try:
            account = TwitterAccount.run(
                auth_token=self.account.auth_token,
                setup_session=True,
                proxy=self.account.proxy,
            )
            bind_data = account.bind_account_v1(
                BindAccountParamsV1(
                    url="https://api.nyanheroes.com/Login/Authorize?callbackUrl=https://missions.nyanheroes.com/"
                )
            )

            params = {
                "callbackUrl": bind_data.url,
                "oauthToken": bind_data.oauth_token,
                "oauthVerifier": bind_data.oauth_verifier,
            }

            response = await self.get(
                f"https://api.nyanheroes.com/Login/Authorize?callbackUrl={bind_data.url}",
                allow_redirects=True,
                params=params,
            )
            response.raise_for_status()

            if not response.json().get("token"):
                # raise APIError("Failed to login, twitter account might be invalid")
                logger.error(
                    f"Account: {self.account.auth_token} | Failed to login via twitter: account might be invalid | Skip.."
                )
                return False

            self.headers["authorization"] = f"Bearer {response.json()['token']}"
            logger.success(
                f"Account: {self.account.auth_token} | Logged in successfully: {self.wallet.get_address}"
            )
            return True

        except Exception as error:
            # raise APIError(f"Account: {self.account.auth_token} | Failed to login via twitter: {error}")
            logger.error(
                f"Account: {self.account.auth_token} | Failed to login via twitter: {error} | Skip.."
            )
            return False

    async def get_quests(self) -> list[dict]:
        response = await self.send_request(
            method="/Quest/getQuests", request_type="GET"
        )
        return response["quests"]

    async def bind_referral_code(self) -> dict:
        try:
            params = {
                "referralCode": config.referral_code,
            }

            response = await self.send_request(
                method="/User/addReferral",
                params=params,
            )
            logger.success(
                f"Account: {self.account.auth_token} | Referral code bound successfully"
            )
            return response

        except Exception as error:
            logger.error(
                f"Account: {self.account.auth_token} | Failed to bind referral code: {error}"
            )

    async def complete_quests(self) -> bool:

        async def join_nyan_newsletter() -> None:
            try:
                json_data = {
                    "QuestId": 86,
                    "Email": generate_random_email(),
                    "FirstName": names.get_first_name(),
                    "LastName": names.get_last_name(),
                }

                await self.send_request(
                    method="/Quest/registerForNewsletter", json_data=json_data
                )
                logger.success(
                    f"Account: {self.account.auth_token} | Completed quest: Join Nyan Newsletter | Category: newsletter"
                )

            except Exception as error:
                logger.error(
                    f"Account: {self.account.auth_token} | Failed to complete quest: Join Nyan Newsletter | Category: newsletter | Error: {error}"
                )

        async def set_quest(quest_data: dict) -> None:
            try:
                json_data = {
                    "Id": quest_data["id"],
                    "WalletAddress": "",
                }

                if quest_data["category"] in config.ignored_quests_categories:
                    logger.warning(
                        f"Account: {self.account.auth_token} | Ignored quest: {quest_data['title']} | Category: {quest_data['category']}"
                    )

                else:
                    await self.send_request(
                        method="/Quest/setQuests", json_data=json_data
                    )
                    logger.success(
                        f"Account: {self.account.auth_token} | Quest completed: {quest_data['title']} | Category: {quest_data['category']}"
                    )

            except Exception as error:
                logger.error(
                    f"Account: {self.account.auth_token} | Failed to complete quest: {quest_data['title']} | Category: {quest_data['category']} | Error: {error}"
                )

        try:
            quests = await self.get_quests()
            await self.bind_referral_code()
            await self.bind_wallet()

            for quest in quests:
                if quest["category"] == "newsletter":
                    await join_nyan_newsletter()
                else:
                    await set_quest(quest)

                await asyncio.sleep(config.timeout_between_quests)

            return True

        except Exception as error:
            logger.error(
                f"Account: {self.account.auth_token} | Failed to complete quests: {error} | Skip.."
            )
            return False

    async def export_account(self, success: bool = True):
        if success:
            accounts_path = os.path.join(os.getcwd().replace('//src', ''), "config", "success_accounts.txt")
        else:
            accounts_path = os.path.join(os.getcwd().replace('//src', ''), "config", "failed_accounts.txt")

        async with aiofiles.open(accounts_path, "a") as file:
            await file.write(f"{self.account.auth_token}|{self.wallet.get_mnemonic}\n")


    async def start(self):
        logger.info(f"Account: {self.account.auth_token} | Processing...")
        if not await self.login():
            await self.export_account(success=False)
            return

        if not await self.complete_quests():
            await self.export_account(success=False)
            return

        logger.success(f"Account: {self.account.auth_token} | Quests completed successfully")
        await self.export_account(success=True)
