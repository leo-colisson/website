import os

##### These functions are provided if you want to test your code with the AES block cipher
# Do NOT use these libraries in your code. I just import them here to get access to AES
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def aes_cipher(key, message):
    aes_cipher = Cipher(algorithms.AES(key), modes.ECB()) # ECB applique juste AES bloc par bloc
    encryptor = aes_cipher.encryptor()
    return encryptor.update(message) + encryptor.finalize()

def aes_decipher(key, ciphertext_block):
    aes_cipher = Cipher(algorithms.AES(key), modes.ECB())
    decryptor = aes_cipher.decryptor()
    return decryptor.update(ciphertext_block) + decryptor.finalize()


##### You should write the definitions of these functions

def gen_key():
    """Generate a key for the AES cipher of length 256 bits. You should use os.urandom(X) to generate X random bytes."""
    pass

def cbc_ansix923_enc(cipher, decipher, key, message):
    """
    You should implement the CBC mode using the cipher provided in parameters:
    - cipher is a function that you can call like cipher(key, message), typically AES. It expects a key of 256 bits (you can use os.urandom(X) to generate X random bytes (not bits)). message is also a bytes, but has 128 bits. You can generate bytes with b'your text'.
    - decipher: like cipher, but inverse function
    - message is the message to encrypt (type bytes, see above line for details), of arbitrary length.
    - key is a key (same type as the input of cipher)
    """
    pass

def cbc_ansix923_dec(cipher, decipher, key, ciphertext):
    """
    Déchiffre un message chiffré avec CBC + padding ANSI X.923.
    """
    pass

def padding_oracle_attack(oracle, ciphertext):
    """
    Your code may call oracle(ciphertext) (where ciphertext has
    type bytes) to receive True if ciphertext is valid (padding is
    correct) and False otherwise. You should return the decrypted ciphertext.
    """
    pass
