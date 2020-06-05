import socket

class TcpSocketConnector:
    
    def __init__(self, callback, ip, port, buffer_size=4096):
        self.callback = callback
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))
        self.buffer_size = buffer_size
        self.run = True
    
    def start(self):
        while self.run:
            data = self.client_socket.recv(self.buffer_size)
            self.callback(data)
    
    def stop(self):
        self.run = False
        self.client_socket.close()

class UdpSocketConnector:
    
    def __init__(self, callback, ip, port, buffer_size=4096):
        self.callback = callback
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.buffer_size = buffer_size
        self.run = True
    
    def start(self):
        while self.run:
            data, _ = self.sock.recvfrom(self.buffer_size)
            self.callback(data)
    
    def stop(self):
        self.run = False        
        self.sock.close()

def callback(data):
    print data

def test_tcp_socket():
    ip_server = "192.168.0.1"
    port_server = 11234    
    socket_connector = TcpSocketConnector(callback, ip_server, port_server)
    socket_connector.start()

def test_udp_socket():
    ip_destination = "192.168.0.2"
    port_destination = 11234
    socket_connector = UdpSocketConnector(callback, ip_destination, port_destination)
    socket_connector.start()

def main():
    test_udp_socket()
    #test_tcp_socket()
    
if __name__ == "__main__":
    main()
