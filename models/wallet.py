from pydantic import BaseModel
from solders.signature import Signature


class SignatureData(BaseModel):
    message: str
    signature: Signature

    model_config = {
        "arbitrary_types_allowed": True,
    }
