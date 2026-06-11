from slowapi import Limiter
from slowapi.util import get_remote_address

# Configure the SlowAPI limiter to track clients by remote IP address.
# A default rate limit of 60 requests per minute is applied globally.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60 per minute"]
)
