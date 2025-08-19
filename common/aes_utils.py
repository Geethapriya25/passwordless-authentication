from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64

# Load AES key from environment variable (hex string) and convert to bytes
key_hex = os.getenv("AES_SECRET_KEY")
if not key_hex:
    raise ValueError("AES_SECRET_KEY environment variable not set!")
if len(key_hex) != 64:  # 32 bytes * 2 hex chars per byte = 64 chars
    raise ValueError("AES_SECRET_KEY must be 64 hex characters (32 bytes) long!")
KEY = bytes.fromhex(key_hex)  # convert hex string to bytes

def encrypt_data(plaintext: str) -> str:
    backend = default_backend()
    iv = os.urandom(16)  # 16 bytes IV for AES-CBC

    # Pad plaintext to block size (128 bits)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Return base64 encoded iv + ciphertext
    encrypted = base64.b64encode(iv + ciphertext).decode('utf-8')
    return encrypted

def decrypt_data(ciphertext_b64: str) -> str:
    backend = default_backend()
    data = base64.b64decode(ciphertext_b64.encode())

    iv = data[:16]
    ciphertext = data[16:]

    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad plaintext
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext.decode('utf-8')