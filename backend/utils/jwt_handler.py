import jwt
import datetime
from config import Config

def create_jwt(payload, expires_in=3600):
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
    return token

def decode_jwt(token):
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
