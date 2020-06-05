from charm.schemes.ibenc.ibenc_waters09 import DSE09
from charm.toolbox.pairinggroup import PairingGroup, GT

def encrypt(data, mpk, ID):
    data = grp.random(GT)
    print "plain data: ", data
    ct = ibe.encrypt(mpk, data, ID)
    return ct

def decrypt(ct, mpk, msk, ID):
    sk = ibe.keygen(mpk, msk, ID)
    m = ibe.decrypt(ct, sk)
    print "plain data: ", m

ID = "user2@email.com"
data = "hello world"

grp = PairingGroup('SS512')
ibe = DSE09(grp)
(mpk, msk) = ibe.setup()
ct = encrypt(mpk, ID)

#grp = None
ibe = None
mpk = None
msk = None
#grp = PairingGroup('SS512')
ibe = DSE09(grp)
(mpk, msk) = ibe.setup()
decrypt(ct, mpk, msk, ID)