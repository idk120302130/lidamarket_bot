import hashlib
import hmac
import json
from urllib.parse import parse_qsl
from config import BOT_TOKEN

def validate_init_data(init_data: str) -> dict | None:
    """
    Validates Telegram WebApp initData and returns parsed user info.
    Returns None if validation fails.
    """
    try:
        parsed_data = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None
        
    if "hash" not in parsed_data:
        return None

    hash_ = parsed_data.pop("hash")
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items())
    )
    
    secret_key = hmac.new(
        key=b"WebAppData", msg=BOT_TOKEN.encode(), digestmod=hashlib.sha256
    ).digest()
    
    calculated_hash = hmac.new(
        key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    if calculated_hash != hash_:
        return None
        
    if "user" in parsed_data:
        return json.loads(parsed_data["user"])
    return None
