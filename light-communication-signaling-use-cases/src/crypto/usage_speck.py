from speck import SpeckCipher
import struct

def client_server_test():
    block_size = 128
    key_token = 123456 # shared via VLC
        
    speck_server = SpeckCipher(key_token, block_size=block_size)
    
    counter = 0
    cipher_server = speck_server.encrypt(counter)
    print cipher_server
    
    speck_client = SpeckCipher(key_token, block_size=block_size)
    plain_client = speck_client.decrypt(cipher_server)
    print plain_client
    
    plain_client += 1
    cipher_client = speck_client.encrypt(plain_client)
    print cipher_client
    
    plain_server = speck_server.decrypt(cipher_client)
    print plain_server
    
    assert plain_server > counter

def chunks(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def decode_hex_bytes(hex_bytes):
    c = bytearray.fromhex(hex_bytes)
    base = ">i"
    pad = ""
    while struct.calcsize(base + pad) != len(c):
        pad += "x"
    return struct.unpack(base + pad, c)[0]

def main():
    client_server_test()
    
if __name__ == "__main__":
    main()
