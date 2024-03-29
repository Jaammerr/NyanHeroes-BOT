from datetime import datetime, timezone
from solders.keypair import Keypair
from mnemonic import Mnemonic

from models import SignatureData


class Wallet:
    def __init__(self, mnemonic: str = None):
        self.mnemonic = mnemonic
        self.keypair = self.get_keypair()

    @property
    def get_address(self) -> str:
        return str(self.keypair.pubkey())

    @property
    def get_mnemonic(self) -> str:
        return self.mnemonic

    def get_keypair(self) -> Keypair:
        mnemo = Mnemonic("english")
        if self.mnemonic:
            seed = mnemo.to_seed(self.mnemonic)
        else:
            self.mnemonic = mnemo.generate()
            seed = mnemo.to_seed(self.mnemonic)

        keypair = Keypair.from_seed_and_derivation_path(seed, "m/44'/501'/0'/0")
        return keypair

    @staticmethod
    def get_timestamp() -> str:
        now = datetime.now(timezone.utc)
        formatted_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return formatted_timestamp

    def get_message(self) -> str:
        ts = self.get_timestamp()
        return f"Please sign in to prove the ownership : {self.keypair.pubkey()} , Timestamp: {ts}"

    def sign_message(self) -> SignatureData:
        message = self.get_message()
        encoded_message = message.encode("utf-8")
        signature = self.keypair.sign_message(encoded_message)
        return SignatureData(message=message, signature=signature)
