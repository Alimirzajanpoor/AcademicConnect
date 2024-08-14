from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()
schemes_algorithm = os.getenv("schemes_algorithm")
pwd_context = CryptContext(schemes=[schemes_algorithm], deprecated="auto")


class Hash:
    def bcrypt(password: str):
        return pwd_context.hash(password)

    def verify(hashed_password, plain_password):
        return pwd_context.verify(plain_password, hashed_password)
