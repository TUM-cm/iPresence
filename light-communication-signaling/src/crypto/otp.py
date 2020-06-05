import pyotp
import time

class OneTimePass(object):
    
    def __init__(self, interval=30, token_len=6):
        self.interval = interval
        self.secret = pyotp.random_base32()
        self.totp = pyotp.TOTP(self.secret, interval=self.interval, digits=token_len)
    
    def get_token(self):
        return self.totp.now()
    
    def verify_token(self, token):
        return self.totp.verify(token)
    
    def get_secret(self):
        return self.secret
    
    def get_interval(self):
        return self.interval

def main():    
    totp = OneTimePass(interval=600, token_len=8)
    print totp.get_token()
    
    secret = pyotp.random_base32()
    # within validity period getting same token
    totp = pyotp.TOTP(secret, interval=1, digits=8)
    print totp.now()
    time.sleep(1)
    print totp.now()
     
    limit = 3
    counter = 0
    print "pyotp"
    while counter < limit:
        print time.strftime("%H:%M:%S")
        totp = pyotp.TOTP(secret, interval=10, digits=8)
        token = totp.now()
        print "token: ", token
        result = totp.verify(token)
        print "result: ", result
        while totp.verify(token):
            pass
        counter += 1
    print time.strftime("%H:%M:%S")

if __name__ == "__main__":
    main()
