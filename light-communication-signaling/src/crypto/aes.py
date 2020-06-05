import nonce
import base64
import random
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]

class AESCipher(object):
    
    def __init__(self, key, encode=base64.b64encode, decode=base64.b64decode):
        self.key = key
        self.mode = AES.MODE_CBC
        self.encode = encode
        self.decode = decode
    
    @classmethod
    def keyFromFile(cls, keypath):        
        key = AESCipher.load_key(keypath)
        return cls(key)
    
    @classmethod
    def keyFromGen(cls, encode, decode):
        password = AESCipher.generate_password()
        key = cls.create_key(password)
        return cls(key, encode, decode), password
    
    @classmethod
    def keyFromVariable(cls, pw, encode, decode):
        return cls(cls.create_key(pw), encode, decode)
    
    @classmethod
    def keyFromPassword(cls, password):
        key = cls.create_key(password.encode())
        return cls(key)
    
    def encrypt(self, data):
        if data and len(data) > 0:
            message = pad(data)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return self.encode(iv + cipher.encrypt(message)).decode("utf-8")
        else:
            return data
    
    def decrypt(self, data):
        if data and len(data) > 0:        
            enc = self.decode(data)
            iv = enc[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
        else:
            return data
    
    def save_key(self, filepath):
        f = open(filepath, "wb")
        f.write(self.key)
        f.close()
    
    @staticmethod
    def generate_fixed_password(pwd_len=32):
        password = ''
        for _ in range(int(pwd_len)):
            password += chr(random.randint(33,126))
        return password
    
    @staticmethod
    def generate_password():    
        return nonce.gen_nonce_uuid4()
    
    @staticmethod 
    def load_key(keypath):
        f = open(keypath, "rb")
        data = f.read()
        f.close()
        return data
    
    @staticmethod
    def load_password(filepath):
        f = open(filepath, "r")
        data = f.read()
        f.close()
        return data
    
    @staticmethod
    def create_key(password):
        return hashlib.sha256(password).digest()

def main():
    pwd = AESCipher.generate_fixed_password()
    print(pwd)
    print(len(pwd))
    
    pwd = AESCipher.generate_password()
    print(pwd)
    print(len(pwd))
    
    aes = AESCipher.keyFromPassword(pwd)
    cipher = aes.encrypt("hello world")
    print(cipher)
    print(aes.decrypt(cipher))
    
if __name__ == "__main__":
    main()
