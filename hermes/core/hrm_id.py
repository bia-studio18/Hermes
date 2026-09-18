import secrets
import time


BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def base62_encode(number: int) -> str:
    if number == 0:
        return BASE62[0]

    result = []

    while number:
        number, remainder = divmod(number, 62)
        result.append(BASE62[remainder])

    return "".join(reversed(result))


def hrm_id(entity_type: str) -> str:
    timestamp = int(time.time() * 1000)

    random_bits = secrets.randbits(76)

    value = (
        (timestamp << 80)
        | (0x7 << 76)
        | random_bits
    )

    encoded = base62_encode(value)

    encoded = encoded.zfill(22)

    return f"HRM-{entity_type.upper()}-{encoded.upper()}"