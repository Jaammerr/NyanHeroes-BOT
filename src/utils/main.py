import random
import string


def generate_random_email() -> str:
    domain = "@gmail.com"
    username_length = random.randint(5, 10)
    username = "".join(
        random.choice(string.ascii_lowercase) for _ in range(username_length)
    )
    return username + domain
