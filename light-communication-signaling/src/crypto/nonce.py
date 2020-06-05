import base64
import os
import uuid
from hashlib import sha1
from random import random, SystemRandom

def gen_nonce_sha1():
    return sha1(str(random())).hexdigest()

def gen_nonce_uuid4():
    return uuid.uuid4().hex

def gen_nonce_sys(length=8):
    return ''.join([str(SystemRandom().randint(0, 9)) for _ in range(length)])

def gen_nonce_length(length=32):
    string = base64.b64encode(os.urandom(length), altchars = b'-_')
    return string[0:length].decode()

if __name__ == "__main__":
    pwd_len = []
    for _ in range(1000):
        pwd_len.append(len(uuid.uuid4().hex))
    print(pwd_len)
    
    print gen_nonce_length()
    print gen_nonce_sha1()
    print gen_nonce_uuid4()
    print gen_nonce_sys()
