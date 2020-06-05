import hashlib
import uuid

# http://jasonwyatt.co/post/40138193838/generate-hashed-passwords-and-salts-with-python

def hash_secret(secret, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
    hashed_secret = hashlib.sha512(salt + secret).hexdigest()
    return (salt, hashed_secret)

def verify_secret(secret, hashed_secret, salt):
    salt, re_hashed = hash_secret(secret, salt)
    return re_hashed == hashed_secret

def main():
    user = "admin"
    password = "password"
    print "user"
    print "%s:%s" % hash_secret(user)
    print "pw"
    print "%s:%s" % hash_secret(password)
    
if __name__ == "__main__":
    main()