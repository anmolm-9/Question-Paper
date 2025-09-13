import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://anmol09m:G4xuXlDjdLkByRbe@anmol.dwzkumt.mongodb.net/?retryWrites=true&w=majority&appName=Anmol")
    DB_NAME = os.getenv("DB_NAME", "question_paper_db")

    JWT_SECRET = os.getenv("JWT_SECRET", "change-this")
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5500")

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    MAIL_FROM  = os.getenv("MAIL_FROM", "Question Papers <no-reply@example.com>")
