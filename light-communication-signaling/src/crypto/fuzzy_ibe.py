from charm.schemes.ibenc.ibenc_sw05 import IBE_SW05_LUC
from charm.toolbox.pairinggroup import PairingGroup, GT

groupObj = PairingGroup('SS512')
n = 6
d = 4

ibe = IBE_SW05_LUC(groupObj)
(pk, mk) = ibe.setup(n, d)

w = ['insurance', 'id=2345', 'doctor', 'oncology', 'nurse', 'JHU']  # private identity
wPrime = ['insurance', 'id=2345', 'doctor', 'oncology', 'JHU', 'billing', 'misc']  # public identity for encrypt

(w_hashed, sk) = ibe.extract(mk, w, pk, d, n)

M = groupObj.random(GT)
print "plain data: ", M
cipher = ibe.encrypt(pk, wPrime, M, n)
m = ibe.decrypt(pk, sk, cipher, w_hashed, d)
print "plain data: ", m
