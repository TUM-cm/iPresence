import socket
import utils.times as times
try:
    import crypto.nonce as nonce
    from crypto.aes import AESCipher
    from crypto.speck_wrapper import Speck
except:
    pass

class TcpSocketTestServer:
    
    def __init__(self, port, test_data, control, ip=''):
        self.test_data = test_data
        self.server_address = (ip, port)
        self.run = True
        self.control = control
    
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        self.sock.listen(1)
        print("listening ...")
        while self.run:
            connection, _ = self.sock.accept()
            try:
                while self.run:
                    if self.control:
                        self.control.send_timestamp = times.get_timestamp()
                        self.run = False
                    connection.sendall(self.test_data)
                connection.close()
            except:
                connection.close()
    
    def stop(self):
        self.run = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        sock.close()

class UdpSocketTestServer:
    
    def __init__(self, ip, port, test_data):
        self.test_data = test_data
        self.server_address = (ip, port)
        self.run = True
    
    def start(self):
        print("running ...")
        while self.run:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.sendto(self.test_data, self.server_address)
            self.sock.close()
    
    def stop(self):
        self.run = False
        self.sock.close()

class UdpSpeckSocketTestServer:
    
    def __init__(self, ip, port, test_data, key_size=128, block_size=128):
        self.server_address = (ip, port)
        self.test_data = test_data
        self.key_size = key_size
        self.block_size = block_size
        self.key = nonce.gen_nonce_sha1()
        self.speck = Speck(self.key, self.key_size, self.block_size)
        self.parameters = "key=" + str(self.key) + ";" + \
                            "key_size=" + str(self.key_size) + ";" + \
                            "block_size=" + str(self.block_size)
        self.run = True
    
    def start(self):
        print("running ...")
        # send parameters
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.sendto(self.parameters, self.server_address)
        self.sock.close()    
        while self.run:
            self.test_cipher_data = self.speck.encrypt(self.test_data)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.sendto(self.test_cipher_data, self.server_address)
            self.sock.close()
    
    def stop(self):
        self.run = False
        self.sock.close()

class UdpAesSocketTestServer:
    
    def __init__(self, ip, port, test_data):
        self.server_address = (ip, port)
        self.test_data = test_data
        #self.data_counter = 0
        #self.data_limit = 204800        
        #self.len_test_data = len(test_data)
        pwd = AESCipher.generate_password()
        self.parameters = "pwd=" + pwd
        self.aes = AESCipher.keyFromPassword(pwd)
        self.run = True
    
    def start(self):
        print("running ...")
        # send parameters
        print(self.parameters)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.sendto(self.parameters, self.server_address)
        self.sock.close()
        while self.run:
            self.test_cipher_data = self.aes.encrypt(self.test_data)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.sendto(self.test_cipher_data, self.server_address)
            self.sock.close()
            #self.data_counter += self.len_test_data
            #if self.data_counter >= self.data_limit:
            #    print(self.data_counter)
            #    print("stop")
            #    self.stop()
    
    def stop(self):
        self.run = False
        self.sock.close()

def start_tcp_server(port, test_data, control=None):
    socket_test_server = TcpSocketTestServer(port, test_data, control)
    socket_test_server.start()
    
def start_udp_server(ip_destination, port_destination, test_data):
    socket_test_server = UdpSocketTestServer(ip_destination, port_destination, test_data)
    socket_test_server.start()

def start_udp_speck_server(ip_destination, port_destination, test_data):
    socket_test_server = UdpSpeckSocketTestServer(ip_destination, port_destination, test_data)
    socket_test_server.start()

def start_udp_aes_server(ip_destination, port_destination, test_data):
    socket_test_server = UdpAesSocketTestServer(ip_destination, port_destination, test_data)
    socket_test_server.start()

def main():
    port_destination = 11234
    ip_destination = '192.168.0.2'
    test_data = "abcdefghijklmnopqrstuvwxyz0123456789"
    
    #start_tcp_server(port_destination, test_data)
    start_udp_server(ip_destination, port_destination, test_data)
    #start_udp_speck_server(ip_destination, port_destination, test_data)
    #start_udp_aes_server(ip_destination, port_destination, test_data)

if __name__ == "__main__":
    main()
