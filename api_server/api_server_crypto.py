# from hashlib import md5
# import base64
# from Crypto import Random
# from Crypto.Cipher import AES
#
# BLOCK_SIZE=16
# def trans(key):
#     try:
#         theReturn = md5(key).digest()
#     except Exception as Ex:
#         theReturn = md5(key.encode('utf-8')).digest()
#     finally:
#         return theReturn
#
#
# def encrypt(message, passphrase):
#     passphrase = trans(passphrase)
#     IV = Random.new().read(BLOCK_SIZE)
#     aes = AES.new(passphrase, AES.MODE_CFB, IV)
#     return base64.b64encode(IV + aes.encrypt(message))
#
#
# def decrypt(encrypted, passphrase):
#     passphrase = trans(passphrase)
#     encrypted = base64.b64decode(encrypted)
#     IV = encrypted[:BLOCK_SIZE]
#     aes = AES.new(passphrase, AES.MODE_CFB, IV)
#     return aes.decrypt(encrypted[BLOCK_SIZE:])
from Crypto import Random
from Crypto.Cipher import AES
import base64
from hashlib import md5

BLOCK_SIZE = 16

def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length)*length).encode()

def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

def bytes_to_key(data, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]

def encrypt(message, passphrase):
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))


password = "some password".encode()
ct_b64 = "U2FsdGVkX1+ATH716DgsfPGjzmvhr+7+pzYfUzR+25u0D7Z5Lw04IJ+LmvPXJMpz"

pt = decrypt(ct_b64, password)
print("pt", pt)

print("pt", decrypt(encrypt(pt, password), password))
DC=decrypt('U2FsdGVkX18AVpPh2rdsCtQp5C4wOcel1PHC9+6sqFQ=' , 'secret'.encode())

# DC1=encrypt('message' , 'secret')
# print(DC1)
# # DC=decrypt(DC1,'secret')
# print(dir(DC))
print(DC)
print(DC.decode('utf-8'))