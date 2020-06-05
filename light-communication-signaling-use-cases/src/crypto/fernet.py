# from cryptography.fernet import Fernet
# 
# key = Fernet.generate_key()
# f = Fernet(key)
# token = f.encrypt(b"A really secret message. Not for prying eyes.")
# f.decrypt(token)

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_fernet(password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    base64.urlsafe_b64encode(os.urandom(32))
    return Fernet(key)

password = str(123).encode()
secret = "Secret message!"

token = get_fernet(password).encrypt(secret)
print get_fernet(password).decrypt(token)
