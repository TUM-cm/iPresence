import crypto.nonce as nonce
from crypto.speck import SpeckCipher

class Speck(object):
    
    def __init__(self, key, key_size, block_size, delim=":"):
        self.block_size = block_size
        self.delim = delim
        key_int = self.__to_int(str(key))
        self.speck = SpeckCipher(key_int, key_size=key_size, block_size=block_size)
    
    def encrypt(self, message):
        chunksize = self.block_size / 8
        message_str = str(message)
        chunks = (message_str[i:i+chunksize] for i in range(0, len(message_str), chunksize))
        cipher = map(self.__single_encrypt, chunks)
        return self.delim.join(str(x) for x in cipher)
    
    def decrypt(self, raw_data):
        message_parts = raw_data.split(self.delim)
        return "".join(map(self.__single_decrypt, message_parts))
    
    def __single_encrypt(self, message):
        message_int = self.__to_int(message)
        return self.speck.encrypt(message_int)
    
    def __single_decrypt(self, message_int):
        plaintext_int = self.speck.decrypt(int(message_int))
        return self.__to_value(plaintext_int)
    
    def __to_int(self, message):
        return sum([ord(c) << (8 * x) for x, c in enumerate(reversed(message))])
    
    def __to_value(self, message):
        return bytearray.fromhex('{:02x}'.format(message)).decode()

def main():
    i = 0
    while i < 100:
        key = nonce.gen_nonce_sha1()
        print "key: ", key
        speck = Speck(key, 128, 128)
        value = "hello world abc def hello"
        cipher = speck.encrypt(value)
        plain = speck.decrypt(cipher)
        assert str(value) == str(plain)
        print "cipher: ", cipher
        print "plain: ", plain
        i += 1

if __name__ == "__main__":
    main()
