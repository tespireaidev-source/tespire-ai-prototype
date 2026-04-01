from jose import jwt, JWTError, ExpiredSignatureError
import os


SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not SUPABASE_JWT_SECRET:
    raise RuntimeError("SUPABASE_JWT_SECRET is not set")


def verify_token(token: str):
    """
    Verifies a Supabase JWT token.

    Args:
        token (str): Bearer token from request

    Returns:
        dict: Decoded payload if valid
        str: "expired" if token expired
        None: if invalid
    """
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"]
        )

        return payload

    except ExpiredSignatureError:
        return "expired"

    except JWTError:
        return None