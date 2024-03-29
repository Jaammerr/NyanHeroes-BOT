import asyncio

from config import load_config
from models import Config

config: Config = load_config()
semaphore = asyncio.Semaphore(config.threads)
