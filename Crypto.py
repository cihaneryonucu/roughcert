import ed25519, cryptography
from pyroughtime import RoughtimeClient, RoughtimeServer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def generate_private_key(filename):
    # Gen private key, n=65537, 2048 keysize
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    # Write key to a file
    with open(filename, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(b"password") # todo: Change this with param
            )
        )

    return key


