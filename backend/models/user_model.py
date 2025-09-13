from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from email_validator import validate_email, EmailNotValidError
import bcrypt
from config import Config 

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]
users = db["users"]

users.create_index([("email", ASCENDING)], unique=True)

def _hash_password(password: str) -> bytes:
    rounds = max(8, int(Config.BCRYPT_ROUNDS))
    salt = bcrypt.gensalt(rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt)

def _check_password(hashed: bytes, password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed)
    except Exception:
        return False

def validate_and_normalize_email(email: str) -> str:
    try:
        v = validate_email(email)
        return v.normalized
    except EmailNotValidError as e:
        raise ValueError(str(e))

def create_user(first_name, last_name, email, password, phone=None, role="user"):
    email_norm = validate_and_normalize_email(email)
    pwd_hash = _hash_password(password)
    doc = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email_norm,
        "password": pwd_hash,      
        "phone": phone,
        "role": role,             
        "isActive": True,
        "isEmailVerified": True,   
        "usageStats": {"lastLogin": None, "totalLogins": 0}
    }
    res = users.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def find_user_by_email(email: str):
    email_norm = validate_and_normalize_email(email)
    return users.find_one({"email": email_norm})


def find_user_by_id(user_id: str):
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def verify_password(stored_hash, password: str) -> bool:
    return _check_password(stored_hash, password)


def update_user(query, update_fields):
    return users.update_one(query, {"$set": update_fields})


def to_safe_user(doc):
    if not doc:
        return None
    return {
        "id": str(doc["_id"]),
        "firstName": doc.get("firstName"),
        "lastName": doc.get("lastName"),
        "email": doc.get("email"),
        "phone": doc.get("phone"),
        "role": doc.get("role", "user"),
        "isActive": doc.get("isActive", True),
        "isEmailVerified": doc.get("isEmailVerified", False),
        "usageStats": doc.get("usageStats", {}),
    }
